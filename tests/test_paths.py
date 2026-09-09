"""Folder/path regression matrix.

Every test here reproduces a real defect in which Lobster resolved a path
against the wrong authority (process cwd, or a caller-supplied string joined
without containment) instead of against the single resolved target root.
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


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class PathAuthorityTests(unittest.TestCase):
    """The golden project is the only fixture that exercises the full v3 chain."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.origin = Path.cwd()
        self.addCleanup(os.chdir, self.origin)
        self.outside = self.base / "OUTSIDE"
        self.outside.mkdir()
        self.victim = self.outside / "secret.txt"
        self.victim.write_text("SECRET", encoding="utf-8")

    def project(self, name="project"):
        target = self.base / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(GOLDEN, target)
        return target

    @staticmethod
    def read(path):
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))

    @staticmethod
    def write(path, value):
        Path(path).write_text(json.dumps(value, indent=2), encoding="utf-8")

    def rechain(self, project, field, mutate):
        """Mutate a child artifact and refresh the receipt hash, as an honest author would."""
        receipt_path = project / "receipt-final.json"
        receipt = self.read(receipt_path)
        artifact = project / receipt[field]["path"]
        record = self.read(artifact)
        mutate(record)
        self.write(artifact, record)
        receipt[field]["sha256"] = sha256_of(artifact)
        self.write(receipt_path, receipt)
        return receipt_path

    def verify(self, project, receipt_path=None):
        receipt = self.read(receipt_path or project / "receipt-final.json")
        return lobster.v3_verify(receipt, project)

    # --- baseline -----------------------------------------------------------

    def test_golden_project_is_delivery_ready(self):
        self.assertEqual(self.verify(self.project())["status"], "DELIVERY_READY")

    # --- I7: subdirectories stay inside the permitted workspace -------------

    def test_absolute_dependency_node_path_cannot_escape_project(self):
        project = self.project()
        victim = self.victim

        def mutate(graph):
            node = dict(graph["nodes"][0])
            node["path"] = str(victim)
            node["sha256"] = sha256_of(victim)
            graph["nodes"].append(node)

        self.rechain(project, "dependency_graph", mutate)
        result = self.verify(project)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any(issue.startswith("LOBSTER_PATH_ESCAPES_PROJECT") for issue in result["issues"]),
                        result["issues"])

    def test_traversal_dependency_node_path_cannot_escape_project(self):
        project = self.project()

        def mutate(graph):
            node = dict(graph["nodes"][0])
            node["path"] = "../OUTSIDE/secret.txt"
            node["sha256"] = sha256_of(self.victim)
            graph["nodes"].append(node)

        self.rechain(project, "dependency_graph", mutate)
        result = self.verify(project)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any(issue.startswith("LOBSTER_PATH_ESCAPES_PROJECT") for issue in result["issues"]),
                        result["issues"])

    def test_absolute_evidence_artifact_path_cannot_escape_project(self):
        project = self.project()
        victim = self.victim

        def mutate(manifest):
            manifest["evidence"][0]["path"] = str(victim)
            manifest["evidence"][0]["sha256"] = sha256_of(victim)

        self.rechain(project, "evidence_manifest", mutate)
        result = self.verify(project)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any(issue.startswith("LOBSTER_PATH_ESCAPES_PROJECT") for issue in result["issues"]),
                        result["issues"])

    def test_absolute_scenario_matrix_reference_cannot_escape_project(self):
        project = self.project()
        receipt_path = project / "receipt-final.json"
        receipt = self.read(receipt_path)
        receipt["scenario_matrix"]["path"] = str(self.victim)
        self.write(receipt_path, receipt)
        result = self.verify(project)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any("project-relative" in issue or "escapes" in issue.lower() for issue in result["issues"]),
                        result["issues"])

    # --- I5/I6: the process cwd never selects the target project ------------

    def test_keeps_target_root_stable_when_invocation_cwd_differs(self):
        project = self.project()
        decoy = self.project("decoy")
        (decoy / "tokens.css").write_text("/* decoy */", encoding="utf-8")
        os.chdir(decoy)
        self.assertEqual(self.verify(project)["status"], "DELIVERY_READY")
        os.chdir(self.base)
        self.assertEqual(self.verify(project)["status"], "DELIVERY_READY")

    def test_duplicate_roots_never_touch_the_other_project(self):
        clean = self.project("a/project")
        mutated = self.project("b/project")
        (mutated / "tokens.css").write_text("/* mutated */", encoding="utf-8")
        self.assertEqual(self.verify(clean)["status"], "DELIVERY_READY")
        result = self.verify(mutated)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(any("tokens.css" in issue for issue in result["issues"]), result["issues"])

    def test_cli_relative_project_resolves_against_invocation_cwd(self):
        project = self.project()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", "project/receipt-final.json", "--project", "project"],
            capture_output=True, text=True, cwd=self.base)
        self.assertEqual(json.loads(result.stdout)["status"], "DELIVERY_READY", result.stdout + result.stderr)

    # --- shape of the root itself -------------------------------------------

    def test_spaces_unicode_nesting_and_hidden_directories_verify(self):
        for name in ("foo bar", "área", "a/b/c/d/e", ".hidden", "café — v2"):
            with self.subTest(name=name):
                self.assertEqual(self.verify(self.project(name))["status"], "DELIVERY_READY")

    def test_trailing_separator_on_project_is_accepted(self):
        project = self.project()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", str(project / "receipt-final.json"),
             "--project", str(project) + os.sep],
            capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["status"], "DELIVERY_READY", result.stdout + result.stderr)

    # --- I8: filesystem errors name the operation and the path --------------

    def test_missing_project_error_names_operation_and_path(self):
        missing = self.base / "does-not-exist"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", str(self.project() / "receipt-final.json"),
             "--project", str(missing)], capture_output=True, text=True)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload.get("operation"), "resolve-project-root")
        self.assertEqual(payload.get("path"), str(missing))
        self.assertEqual(result.returncode, 2)

    def test_file_used_as_project_is_rejected_with_context(self):
        target = self.base / "a-file.txt"
        target.write_text("x", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", str(self.project() / "receipt-final.json"),
             "--project", str(target)], capture_output=True, text=True)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload.get("operation"), "resolve-project-root")


class RootSpellingInvarianceTests(unittest.TestCase):
    """Same physical root -> same containment decision, however the root is spelled.

    Regression for the Windows CI failure at commit d4fd42a: `contain()` resolved the
    candidate but compared it against the root exactly as given. A root spelled
    non-canonically - a junction or reparse point, or an 8.3 short name such as the
    `RUNNER~1` temporary directories GitHub Actions hands out on Windows - therefore
    compared unequal to itself, and a legitimate project-relative path was refused as
    an escape. Locally the temp directory happened to be canonical, so the suite passed
    and only the Windows CI legs failed.
    """

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.real = self.base / "realroot"
        (self.real / "src").mkdir(parents=True)
        (self.real / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")
        (self.real / "src" / "app.tsx").write_text("export default 1", encoding="utf-8")
        self.outside = self.base / "outside"
        self.outside.mkdir()
        (self.outside / "secret.txt").write_text("SECRET", encoding="utf-8")

    def alias(self):
        """A junction pointing at the real root, i.e. a non-canonical spelling of it."""
        link = self.base / "aliasroot"
        try:
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(self.real)],
                           capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("cannot create a junction in this environment")
        self.assertNotEqual(str(link), str(link.resolve()), "the alias must be non-canonical")
        return link

    def roots(self):
        """The same physical root, spelled every way a caller might supply it."""
        return {
            "raw": self.real,
            "resolved": self.real.resolve(),
            "project_root": lobster.project_root(self.real),
            "trailing-separator": Path(str(self.real) + os.sep),
            "dot-segment": self.real / "." ,
            "alias": self.alias(),
        }

    def test_accepted_paths_are_accepted_through_every_spelling(self):
        for label, root in self.roots().items():
            for relative in ("index.html", "src/app.tsx", "src\\app.tsx"):
                with self.subTest(root=label, relative=relative):
                    path, reason = lobster.contain(root, relative)
                    self.assertIsNotNone(path, f"{label}: refused {relative!r} ({reason})")
                    self.assertTrue(path.is_file())

    def test_refused_paths_stay_refused_through_every_spelling(self):
        refused = [str(self.outside / "secret.txt"), "../outside/secret.txt",
                   "..\\outside\\secret.txt", "/etc/passwd", "C:\\Windows\\system32",
                   "src/../../outside/secret.txt", ""]
        for label, root in self.roots().items():
            for relative in refused:
                with self.subTest(root=label, relative=relative):
                    path, reason = lobster.contain(root, relative)
                    self.assertIsNone(path, f"{label}: accepted {relative!r}")
                    self.assertIsNotNone(reason)

    def test_every_spelling_reaches_the_same_physical_file(self):
        results = {label: lobster.contain(root, "src/app.tsx")[0]
                   for label, root in self.roots().items()}
        canonical = {str(path.resolve()) for path in results.values() if path is not None}
        self.assertEqual(len(canonical), 1, f"spellings disagreed on the target: {results}")

    def test_a_symlinked_escape_is_still_refused_through_an_alias_root(self):
        """The alias fix must not weaken containment: resolution still catches escapes."""
        alias = self.alias()
        try:
            subprocess.run(["cmd", "/c", "mklink", "/J", str(self.real / "escape"), str(self.outside)],
                           capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("cannot create a junction in this environment")
        path, reason = lobster.contain(alias, "escape/secret.txt")
        self.assertIsNone(path, "a link out of the project must still escape")
        self.assertEqual(reason, "escapes")


class DependencyGraphPathTests(unittest.TestCase):
    """dependency-graph.mjs must never emit a node outside the project."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.script = PACKAGE / "scripts" / "dependency-graph.mjs"

    def test_relative_import_escaping_project_is_not_a_node(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "leak.css").write_text("body{color:red}", encoding="utf-8")
        project = self.base / "project"
        project.mkdir()
        (project / "index.html").write_text(
            '<link rel="stylesheet" href="../outside/leak.css"><link rel="stylesheet" href="./local.css">',
            encoding="utf-8")
        (project / "local.css").write_text("body{color:blue}", encoding="utf-8")
        out = self.base / "graph.json"
        result = subprocess.run(["node", str(self.script), str(project), "index.html", str(out)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        graph = json.loads(out.read_text(encoding="utf-8"))
        paths = [node["path"] for node in graph["nodes"]]
        self.assertIn("local.css", paths)
        self.assertFalse([path for path in paths if path.startswith("..")], paths)
        self.assertEqual(graph["confidence"], "PARTIAL")
        self.assertTrue(any(item["specifier"] == "../outside/leak.css" for item in graph["unresolved"]),
                        graph["unresolved"])


class BrowserRunnerPathTests(unittest.TestCase):
    """browser-runner.mjs must refuse to write outside the project."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.script = PACKAGE / "scripts" / "browser-runner.mjs"
        self.project = self.base / "project"
        self.project.mkdir()
        (self.project / "index.html").write_text("<h1>ok</h1>", encoding="utf-8")

    def run_matrix(self, matrix, cwd=None):
        matrix_path = self.base / "matrix.json"
        matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
        out = self.base / "run.json"
        return subprocess.run(
            ["node", str(self.script), "--project", str(self.project), "--base-url",
             (self.project / "index.html").as_uri(), "--matrix", str(matrix_path), "--out", str(out)],
            capture_output=True, text=True, cwd=str(cwd or self.base))

    def test_screenshot_path_escaping_project_is_refused_before_launch(self):
        matrix = {"schema": "lobster-scenario-matrix/v1", "scenarios": [
            {"id": "S1", "steps": [{"action": "screenshot", "path": "../escape.png"}]}]}
        result = self.run_matrix(matrix)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        payload = json.loads(result.stderr or result.stdout)
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["operation"], "validate-scenario-matrix")
        self.assertFalse((self.base / "escape.png").exists())

    def test_absolute_screenshot_path_is_refused_before_launch(self):
        matrix = {"schema": "lobster-scenario-matrix/v1", "scenarios": [
            {"id": "S1", "steps": [{"action": "screenshot", "path": str(self.base / "escape.png")}]}]}
        result = self.run_matrix(matrix)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse((self.base / "escape.png").exists())

    @staticmethod
    def playwright_available():
        return subprocess.run(
            ["node", "--input-type=module", "-e",
             "import('playwright').then(()=>process.exit(0)).catch(()=>process.exit(1))"],
            capture_output=True).returncode == 0

    def test_relative_screenshot_path_lands_in_project_not_cwd(self):
        if not self.playwright_available():
            self.skipTest("Playwright is not installed; this proof needs a real browser")
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        matrix = {"schema": "lobster-scenario-matrix/v1", "scenarios": [
            {"id": "S1", "steps": [{"action": "screenshot", "path": "shots/home.png"}]}]}
        result = self.run_matrix(matrix, cwd=elsewhere)
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        self.assertTrue((self.project / "shots" / "home.png").is_file(),
                        f"screenshot not in project; cwd tree: {list(elsewhere.rglob('*'))}")
        self.assertFalse((elsewhere / "shots").exists())


if __name__ == "__main__":
    unittest.main()
