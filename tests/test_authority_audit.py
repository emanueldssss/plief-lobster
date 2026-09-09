"""Is there ANY path that reaches the filesystem without the right authority?

Two complementary proofs:

* static  - every filesystem call site in scripts/ is enumerated and must be on
            the reviewed allowlist below, so a NEW unguarded call site fails CI.
* dynamic - every read performed during a real verify-v3 / verify(v2) / profile
            run is intercepted and must resolve either inside the target project
            root or inside the skill package itself. Nothing else is legitimate.
"""
import ast
import json
import os
import pathlib
import shutil
import tempfile
import unittest
from pathlib import Path

import test_lobster

lobster = test_lobster.lobster
SCRIPT = test_lobster.SCRIPT
PACKAGE = SCRIPT.resolve().parents[1]
GOLDEN = PACKAGE / "golden" / "dashboard-proof"

FS_CALLS = {"read_bytes", "read_text", "write_text", "open", "is_file", "is_dir", "exists",
            "rglob", "glob", "iterdir", "mkdir", "unlink", "stat", "resolve", "expanduser",
            "samefile", "is_relative_to"}

# Every filesystem call site in scripts/lobster.py, with the authority that governs it.
# "package"  - reads the skill's own files, addressed from PACKAGE_ROOT, never from a record.
# "authority"- the resolution/containment primitives themselves.
# "contained"- the path came from a record and passed contain()/RecordCheck.file().
# "cli"      - the path is a CLI argument typed by the operator, who is the authority.
# "config"   - an integration location from env/config, deliberately outside the project.
REVIEWED_FUNCTIONS = {
    "_integration_registry": "package",
    "resolve_integrations": "config",
    "doctor": "package",
    "read_json": "contained",
    "query": "config",
    "discover": "config",
    "verify_implementation": "authority",
    "project_root": "authority",
    "contain": "authority",
    "not_relative": "authority",
    "contained_path": "authority",
    "RecordCheck.__init__": "authority",
    "RecordCheck.file": "authority",
    "auto_profile": "contained",
    "fingerprint_entries": "authority",   # walks only inside the resolved root
    "is_receipt_index": "authority",      # goes through contained_path before reading
    "project_fingerprint": "authority",
    "validate_artifact": "package",
    "v3_verify": "contained",
    "plan": "contained",
    "main": "cli",
}


def enclosing(tree):
    """Map every node to the dotted name of the function that contains it."""
    owner = {}

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}.{child.name}" if prefix else child.name
                owner[child] = name
                walk(child, name)
            else:
                owner[child] = prefix
                walk(child, prefix)

    walk(tree, "")
    return owner


class StaticAuthorityAudit(unittest.TestCase):
    def test_every_filesystem_call_site_is_reviewed(self):
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        owner = enclosing(tree)
        unreviewed = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in FS_CALLS:
                where = owner.get(node, "")
                if not where:
                    continue  # module level is governed by the __file__ rule below
                # nested helpers are governed by their enclosing function
                top = ".".join(where.split(".")[:2]) if where.startswith("RecordCheck") else where.split(".")[0]
                if top not in REVIEWED_FUNCTIONS:
                    unreviewed.append((where or "<module>", node.func.attr, node.lineno))
        self.assertEqual(unreviewed, [],
                         "new unreviewed filesystem call site(s); classify them in "
                         "REVIEWED_FUNCTIONS after checking which authority guards them")

    def test_no_module_level_filesystem_access_outside_the_package_root(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        owner = enclosing(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in FS_CALLS and owner.get(node) == "":
                self.assertIn("__file__", ast.unparse(node),
                              f"module-level filesystem access at line {node.lineno}")

    def test_node_adapters_share_one_containment_module(self):
        for name in ("browser-runner.mjs", "dependency-graph.mjs"):
            source = (PACKAGE / "scripts" / name).read_text(encoding="utf-8")
            self.assertIn("./lib/contain.mjs", source,
                          f"{name} must use the shared containment module, not its own copy")
            self.assertNotIn("function insideProject(", source,
                             f"{name} still defines a private containment rule")


class DynamicAuthorityAudit(unittest.TestCase):
    """Intercept every real read and prove where it landed."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.project = self.base / "project"
        shutil.copytree(GOLDEN, self.project)
        self.outside = self.base / "outside"
        self.outside.mkdir()
        (self.outside / "secret.txt").write_text("SECRET", encoding="utf-8")

    def record_reads(self, call):
        touched = []
        originals = {name: getattr(pathlib.Path, name) for name in ("read_bytes", "read_text", "open")}

        def wrap(name, original):
            def traced(self, *args, **kwargs):
                touched.append(Path(self))
                return original(self, *args, **kwargs)
            return traced

        for name, original in originals.items():
            setattr(pathlib.Path, name, wrap(name, original))
        try:
            call()
        finally:
            for name, original in originals.items():
                setattr(pathlib.Path, name, original)
        return touched

    def assert_all_reads_are_authorised(self, touched, root):
        root = root.resolve()
        package = PACKAGE.resolve()
        stray = []
        for path in touched:
            resolved = Path(os.path.abspath(str(path)))
            if resolved.is_relative_to(root) or resolved.is_relative_to(package):
                continue
            # the operator's own home config is an explicitly documented location
            if resolved.is_relative_to(Path.home() / ".plief"):
                continue
            stray.append(str(resolved))
        self.assertEqual(stray, [], f"read outside project root {root} and package {package}")
        return len(touched)

    def test_v3_verify_reads_only_project_and_package(self):
        receipt = json.loads((self.project / "receipt-final.json").read_text(encoding="utf-8-sig"))
        touched = self.record_reads(lambda: lobster.v3_verify(receipt, self.project))
        count = self.assert_all_reads_are_authorised(touched, self.project)
        self.assertGreater(count, 10, "the interceptor recorded suspiciously few reads")

    def test_v3_verify_under_attack_still_reads_only_project_and_package(self):
        """Every escape spelling at once; not one may reach the filesystem."""
        import hashlib
        victim = self.outside / "secret.txt"
        digest = hashlib.sha256(victim.read_bytes()).hexdigest()
        receipt = json.loads((self.project / "receipt-final.json").read_text(encoding="utf-8-sig"))
        graph_path = self.project / receipt["dependency_graph"]["path"]
        graph = json.loads(graph_path.read_text(encoding="utf-8-sig"))
        for spelling in (str(victim), "../outside/secret.txt", "..\\outside\\secret.txt",
                         "/outside/secret.txt", "a/../../outside/secret.txt"):
            graph["nodes"].append({"path": spelling, "sha256": digest})
        graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        receipt["dependency_graph"]["sha256"] = hashlib.sha256(graph_path.read_bytes()).hexdigest()

        manifest_path = self.project / receipt["evidence_manifest"]["path"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        manifest["evidence"][0]["path"] = str(victim)
        manifest["evidence"][0]["sha256"] = digest
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        receipt["evidence_manifest"]["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

        result = {}
        touched = self.record_reads(
            lambda: result.update(lobster.v3_verify(receipt, self.project)))
        self.assert_all_reads_are_authorised(touched, self.project)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertGreaterEqual(
            sum(1 for i in result["issues"] if i.startswith("LOBSTER_PATH_ESCAPES_PROJECT")), 5,
            result["issues"])

    def test_v2_verify_reads_only_project_and_package(self):
        import copy
        fixture = test_lobster.V2Tests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        touched = self.record_reads(
            lambda: lobster.verify(copy.deepcopy(fixture.receipt), fixture.root))
        self.assert_all_reads_are_authorised(touched, Path(fixture.root))

    def test_auto_profile_reads_only_inside_the_project(self):
        touched = self.record_reads(lambda: lobster.auto_profile(self.project, "dashboard"))
        self.assert_all_reads_are_authorised(touched, self.project)


if __name__ == "__main__":
    unittest.main()
