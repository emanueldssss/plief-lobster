"""lobster-fingerprint/v1 regression matrix.

The project fingerprint used to be recorded and never verified, because writing the
evidence changed the tree it covered. It is now recomputable: the run declares the
exact scope it fingerprinted, that scope may only omit trees another verified hash
chain already covers, and the digest is rebuilt from the files on disk.

These tests prove: determinism, root-independence, cross-implementation equality
with scripts/lib/fingerprint.mjs, tampering detection, and that the scope cannot be
widened to hide a change.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_lobster

lobster = test_lobster.lobster
SCRIPT = test_lobster.SCRIPT
PACKAGE = SCRIPT.resolve().parents[1]
GOLDEN = PACKAGE / "golden" / "dashboard-proof"
FINGERPRINT_MJS = PACKAGE / "scripts" / "lib" / "fingerprint.mjs"


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sample_tree(root: Path):
    """A tree with the shapes that break naive implementations."""
    (root / "src" / "deep").mkdir(parents=True)
    (root / "área").mkdir()
    (root / "with space").mkdir()
    (root / "artifacts" / "final").mkdir(parents=True)
    (root / "proof").mkdir()
    (root / "node_modules" / "pkg").mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "index.html").write_text("<h1>a</h1>", encoding="utf-8")
    (root / "src" / "app.tsx").write_text("export default 1", encoding="utf-8")
    (root / "src" / "deep" / "z z.css").write_text("body{}", encoding="utf-8")
    (root / "área" / "ção.json").write_text('{"a":1}', encoding="utf-8")
    (root / "with space" / "Z.txt").write_text("Z", encoding="utf-8")
    (root / "with space" / "a.txt").write_text("a", encoding="utf-8")
    (root / "artifacts" / "final" / "shot.png").write_bytes(b"EXCLUDED")
    (root / "proof" / "run.json").write_text('{"excluded":true}', encoding="utf-8")
    (root / "node_modules" / "pkg" / "i.js").write_text("module.exports=1", encoding="utf-8")
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    return root


class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.root = sample_tree(self.base / "project")
        self.spec = {"schema": "lobster-fingerprint/v1", "algorithm": "sha256-file-list/v1",
                     "excluded_directories": [".git", "node_modules"],
                     "excluded_paths": ["artifacts", "proof"],
                     "symlink_policy": "record-as-leaf", "file_count": 6}

    def digest(self, root=None, spec=None):
        return lobster.project_fingerprint(root or self.root, spec or self.spec)

    def test_covers_source_and_excludes_generated_and_vendor_trees(self):
        entries = dict(lobster.fingerprint_entries(self.root, self.spec))
        self.assertEqual(sorted(entries), sorted([
            "index.html", "src/app.tsx", "src/deep/z z.css", "área/ção.json",
            "with space/Z.txt", "with space/a.txt"]))

    def test_is_deterministic_across_repeated_runs(self):
        self.assertEqual(self.digest()[0], self.digest()[0])

    def test_is_independent_of_the_project_root_location(self):
        other = sample_tree(self.base / "elsewhere" / "renamed")
        self.assertEqual(self.digest()[0], self.digest(other)[0],
                         "the same content at a different root must fingerprint identically")

    def test_is_independent_of_the_process_cwd(self):
        origin = Path.cwd()
        self.addCleanup(os.chdir, origin)
        first = self.digest()[0]
        os.chdir(self.root)
        self.assertEqual(self.digest()[0], first)

    def test_entry_order_does_not_depend_on_locale(self):
        """Sorting is by UTF-8 bytes; 'Z.txt' must precede 'a.txt' in every locale."""
        entries = [name for name, _ in lobster.fingerprint_entries(self.root, self.spec)]
        self.assertLess(entries.index("with space/Z.txt"), entries.index("with space/a.txt"))

    def test_matches_the_node_implementation_byte_for_byte(self):
        program = f"""
import {{ projectFingerprint }} from {json.dumps(FINGERPRINT_MJS.as_uri())};
console.log(JSON.stringify(projectFingerprint({json.dumps(str(self.root))})));
"""
        result = subprocess.run(["node", "--input-type=module", "-e", program],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        produced = json.loads(result.stdout)
        digest, count = lobster.project_fingerprint(self.root, produced["spec"])
        self.assertEqual(digest, produced["fingerprint"],
                         "the Node runner and the Python verifier disagree on the digest")
        self.assertEqual(count, produced["spec"]["file_count"])

    def test_the_spec_is_bound_into_the_digest(self):
        """A digest cannot be replayed under a different scope."""
        wider = dict(self.spec, excluded_paths=["artifacts", "proof", "src"])
        self.assertNotEqual(self.digest()[0], self.digest(spec=wider)[0])

    def test_symlinked_directory_is_a_leaf_and_is_not_followed(self):
        target = self.base / "outside"
        target.mkdir()
        (target / "leak.txt").write_text("leak", encoding="utf-8")
        try:
            subprocess.run(["cmd", "/c", "mklink", "/J", str(self.root / "linked"), str(target)],
                           capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("cannot create a junction in this environment")
        entries = dict(lobster.fingerprint_entries(self.root, self.spec))
        self.assertEqual(entries.get("linked"), "symlink")
        self.assertNotIn("linked/leak.txt", entries)


class SpecValidationTests(unittest.TestCase):
    BASE = {"schema": "lobster-fingerprint/v1", "algorithm": "sha256-file-list/v1",
            "excluded_directories": [".git", "node_modules"],
            "excluded_paths": ["artifacts", "proof"],
            "symlink_policy": "record-as-leaf", "file_count": 3}

    def test_a_valid_spec_has_no_issues(self):
        self.assertEqual(lobster.fingerprint_spec_issues(self.BASE), [])

    def test_scope_cannot_be_widened_to_hide_source(self):
        for hidden in ("src", "app", ".", "lib"):
            with self.subTest(hidden=hidden):
                spec = dict(self.BASE, excluded_paths=["artifacts", "proof", hidden])
                issues = lobster.fingerprint_spec_issues(spec)
                self.assertTrue(any(i.startswith("LOBSTER_FINGERPRINT_SCOPE_TOO_NARROW") for i in issues),
                                issues)

    def test_excluding_an_arbitrary_directory_name_is_refused(self):
        spec = dict(self.BASE, excluded_directories=[".git", "node_modules", "src"])
        issues = lobster.fingerprint_spec_issues(spec)
        self.assertTrue(any("SCOPE_TOO_NARROW:excluded_directories:src" in i for i in issues), issues)

    def test_the_receipt_index_is_the_only_permitted_extra_exclusion(self):
        """And the allowance is proved from the file's content, never taken on trust."""
        import tempfile, shutil
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        receipt = {"format": "lobster-receipt/v3", "surface": "x", "revision": "r"}
        (base / "receipt-final.json").write_text(json.dumps(receipt), encoding="utf-8")
        (base / "decoy.json").write_text(json.dumps({"not": "the receipt"}), encoding="utf-8")

        spec = dict(self.BASE, excluded_paths=["artifacts", "proof", "receipt-final.json"])
        self.assertEqual(lobster.fingerprint_spec_issues(spec, base, receipt), [],
                         "the receipt under verification may be excluded")
        self.assertTrue(lobster.fingerprint_spec_issues(spec, base, {"a": "different receipt"}),
                        "a file that is not this receipt may not be excluded")
        self.assertTrue(lobster.fingerprint_spec_issues(spec, None, receipt),
                        "without a root the claim cannot be proved, so it is refused")
        decoy = dict(self.BASE, excluded_paths=["artifacts", "proof", "decoy.json"])
        self.assertTrue(lobster.fingerprint_spec_issues(decoy, base, receipt),
                        "an unrelated JSON file cannot pose as the receipt index")
        source = dict(self.BASE, excluded_paths=["artifacts", "proof", "src"])
        self.assertTrue(lobster.fingerprint_spec_issues(source, base, receipt))

    def test_algorithm_and_policy_substitution_is_refused(self):
        for field, value in (("algorithm", "md5"), ("symlink_policy", "follow"),
                             ("schema", "lobster-fingerprint/v0")):
            with self.subTest(field=field):
                issues = lobster.fingerprint_spec_issues(dict(self.BASE, **{field: value}))
                self.assertTrue(any("FINGERPRINT_SPEC_INVALID" in i for i in issues), issues)

    def test_a_missing_spec_is_refused(self):
        self.assertEqual(lobster.fingerprint_spec_issues(None), ["LOBSTER_FINGERPRINT_SPEC_MISSING"])


class TamperingDetectionTests(unittest.TestCase):
    """End-to-end: the golden must notice a change the other chains would miss."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.project = self.base / "project"
        shutil.copytree(GOLDEN, self.project)
        self.receipt_path = self.project / "receipt-final.json"

    def verify(self):
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8-sig"))
        return lobster.v3_verify(receipt, self.project)

    def rechain_run(self, mutate):
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8-sig"))
        run_path = self.project / receipt["scenario_run"]["path"]
        record = json.loads(run_path.read_text(encoding="utf-8-sig"))
        mutate(record)
        run_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        receipt["scenario_run"]["sha256"] = sha256_of(run_path)
        self.receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    def test_golden_is_delivery_ready_with_a_verified_fingerprint(self):
        result = self.verify()
        self.assertEqual(result["status"], "DELIVERY_READY", result["issues"][:5])

    def test_modifying_a_covered_file_outside_the_dependency_graph_is_detected(self):
        """server.py is in the project but is not a dependency-graph node."""
        graph = json.loads((self.project / "proof" / "dependency-graph.json")
                           .read_text(encoding="utf-8-sig"))
        self.assertNotIn("server.py", {node["path"] for node in graph["nodes"]})
        (self.project / "server.py").write_text("# tampered\n", encoding="utf-8")
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("LOBSTER_PROJECT_FINGERPRINT_STALE", result["issues"])
        self.assertEqual(result["computed_stages"]["EXECUTION_VERIFIED"], "FAIL")

    def test_adding_an_untracked_file_to_the_covered_tree_is_detected(self):
        (self.project / "injected.js").write_text("fetch('http://evil')", encoding="utf-8")
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("LOBSTER_PROJECT_FINGERPRINT_STALE", result["issues"])
        self.assertTrue(any(i.startswith("LOBSTER_PROJECT_FINGERPRINT_FILE_COUNT")
                            for i in result["issues"]), result["issues"])

    def test_deleting_a_covered_file_is_detected(self):
        (self.project / "server.py").unlink()
        result = self.verify()
        self.assertIn("LOBSTER_PROJECT_FINGERPRINT_STALE", result["issues"])

    def test_an_excluded_tree_is_still_covered_by_its_own_hash_chain(self):
        """proof/ is outside the fingerprint precisely because the receipt indexes it."""
        (self.project / "proof" / "craft.json").write_text('{"schema":"x"}', encoding="utf-8")
        result = self.verify()
        self.assertNotIn("LOBSTER_PROJECT_FINGERPRINT_STALE", result["issues"],
                         "proof/ must not move the fingerprint")
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any("craft_review" in i for i in result["issues"]), result["issues"][:5])

    def test_widening_the_scope_to_hide_a_change_is_refused(self):
        """The attack: tamper, then re-fingerprint with src excluded."""
        (self.project / "server.py").write_text("# tampered\n", encoding="utf-8")

        def mutate(record):
            spec = dict(record["fingerprint_spec"])
            spec["excluded_paths"] = sorted(set(spec["excluded_paths"]) | {"server.py"})
            record["fingerprint_spec"] = spec

        self.rechain_run(mutate)
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any(i.startswith("LOBSTER_FINGERPRINT_SCOPE_TOO_NARROW")
                            for i in result["issues"]), result["issues"])

    def test_a_forged_file_count_does_not_pass(self):
        (self.project / "injected.js").write_text("x", encoding="utf-8")
        self.rechain_run(lambda record: record["fingerprint_spec"].update(
            file_count=record["fingerprint_spec"]["file_count"] + 1))
        result = self.verify()
        self.assertIn("LOBSTER_PROJECT_FINGERPRINT_STALE", result["issues"])

    def test_a_runtime_v2_run_cannot_prove_its_fingerprint(self):
        def mutate(record):
            record["schema"] = "lobster-runtime/v2"
            record.pop("fingerprint_spec", None)

        self.rechain_run(mutate)
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any(i.startswith("LOBSTER_PROJECT_FINGERPRINT_UNVERIFIABLE")
                            for i in result["issues"]), result["issues"])

    def test_the_fingerprint_survives_a_project_copy_to_another_root(self):
        moved = self.base / "moved" / "elsewhere"
        moved.parent.mkdir(parents=True)
        shutil.copytree(self.project, moved)
        receipt = json.loads((moved / "receipt-final.json").read_text(encoding="utf-8-sig"))
        result = lobster.v3_verify(receipt, moved)
        self.assertEqual(result["status"], "DELIVERY_READY", result["issues"][:5])


if __name__ == "__main__":
    unittest.main()
