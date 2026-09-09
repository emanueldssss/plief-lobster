"""Closure-pass regression tests.

Covers the contracts that were ambiguous or unproven after the containment repair:
the single-root-resolution invariant (I1), the RECORD_VALID contract, stage
attribution, golden root portability, run-artifact containment, and the
cross-platform equivalence of the containment decision (I10).
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath, PureWindowsPath

import test_lobster

lobster = test_lobster.lobster
SCRIPT = test_lobster.SCRIPT
PACKAGE = SCRIPT.resolve().parents[1]
GOLDEN = PACKAGE / "golden" / "dashboard-proof"


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SingleRootResolutionTests(unittest.TestCase):
    """I1: the target root is resolved exactly once per invocation."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.addCleanup(os.chdir, Path.cwd())
        self.addCleanup(setattr, lobster, "project_root", lobster.project_root)

    def count_resolutions(self, call):
        calls = []
        original = lobster.project_root

        def counting(project):
            calls.append(str(project))
            return original(project)

        lobster.project_root = counting
        try:
            call()
        finally:
            lobster.project_root = original
        return calls

    def test_v2_verify_resolves_the_target_root_exactly_once(self):
        fixture = test_lobster.V2Tests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        calls = self.count_resolutions(
            lambda: lobster.verify(copy.deepcopy(fixture.receipt), fixture.root))
        self.assertEqual(len(calls), 1, f"resolved {len(calls)}x: {calls}")

    def test_v3_verify_resolves_the_target_root_exactly_once(self):
        project = self.base / "project"
        shutil.copytree(GOLDEN, project)
        receipt = json.loads((project / "receipt-final.json").read_text(encoding="utf-8-sig"))
        calls = self.count_resolutions(lambda: lobster.v3_verify(receipt, project))
        self.assertEqual(len(calls), 1, f"resolved {len(calls)}x: {calls}")

    def test_one_invocation_cannot_audit_two_projects(self):
        """The exploit: a cwd change between sub-checks must not move the target."""
        good = self.base / "good" / "project"
        evil = self.base / "evil" / "project"
        fixture = test_lobster.V2Tests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        shutil.copytree(fixture.root, good)
        shutil.copytree(fixture.root, evil)
        for item in evil.rglob("*"):
            if item.is_file():
                item.unlink()

        original = lobster.project_root
        seen = []

        def flipping(project):
            root = original(project)
            seen.append(root)
            os.chdir(self.base / "evil")  # a concurrent chdir lands here
            return root

        os.chdir(self.base / "good")
        lobster.project_root = flipping
        try:
            result = lobster.verify(copy.deepcopy(fixture.receipt), Path("project"))
        finally:
            lobster.project_root = original
        self.assertEqual(len(set(seen)), 1, f"one invocation used {len(set(seen))} roots: {seen}")
        self.assertEqual(result["status"], "READY_FOR_REVIEW", result["issues"][:3])


class StageContractTests(unittest.TestCase):
    """RECORD_VALID and cross-artifact stage attribution are contractual, not incidental."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.project = self.base / "project"
        shutil.copytree(GOLDEN, self.project)

    def receipt(self):
        return json.loads((self.project / "receipt-final.json").read_text(encoding="utf-8-sig"))

    def rechain(self, field, mutate):
        receipt = self.receipt()
        artifact = self.project / receipt[field]["path"]
        record = json.loads(artifact.read_text(encoding="utf-8-sig"))
        mutate(record)
        artifact.write_text(json.dumps(record, indent=2), encoding="utf-8")
        receipt[field]["sha256"] = sha256_of(artifact)
        (self.project / "receipt-final.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt

    def stages(self, receipt=None):
        return lobster.v3_verify(receipt or self.receipt(), self.project)

    def test_stage_contract_is_published_in_every_result(self):
        result = self.stages()
        self.assertEqual(set(result["stage_contract"]), set(lobster.V3_STAGES))
        for stage, text in result["stage_contract"].items():
            self.assertTrue(text.strip(), stage)

    def test_record_valid_covers_every_artifact_not_only_the_profile(self):
        """A malformed craft_review is a RECORD failure, not only a craft failure."""
        receipt = self.rechain("craft_review", lambda record: record.pop("schema", None))
        result = self.stages(receipt)
        self.assertEqual(result["computed_stages"]["RECORD_VALID"], "FAIL",
                         "RECORD_VALID must fail when any referenced artifact is malformed")
        self.assertEqual(result["computed_stages"]["CRAFT_REVIEWED"], "FAIL")

    def test_record_valid_fails_when_a_record_names_a_path_outside_the_project(self):
        receipt = self.receipt()
        outside = self.base / "outside.txt"
        outside.write_text("x", encoding="utf-8")

        def mutate(graph):
            node = dict(graph["nodes"][0])
            node["path"] = str(outside)
            node["sha256"] = sha256_of(outside)
            graph["nodes"].append(node)

        receipt = self.rechain("dependency_graph", mutate)
        result = self.stages(receipt)
        self.assertEqual(result["computed_stages"]["RECORD_VALID"], "FAIL")
        self.assertTrue(any(i.startswith("LOBSTER_PATH_ESCAPES_PROJECT") for i in result["issues"]))

    def test_dependency_closure_staleness_is_attributed_to_implementation(self):
        (self.project / "tokens.css").write_text("/* changed */", encoding="utf-8")
        result = self.stages()
        stages = result["computed_stages"]
        self.assertEqual(stages["IMPLEMENTATION_VERIFIED"], "FAIL",
                         "a stale dependency closure belongs to IMPLEMENTATION_VERIFIED")
        self.assertEqual(stages["SOURCE_VERIFIED"], "PASS")
        self.assertEqual(stages["CRAFT_REVIEWED"], "PASS")

    def test_review_binding_staleness_is_attributed_to_craft(self):
        receipt = self.rechain("craft_review", lambda record: record.update(review_input_hash="0" * 64))
        stages = self.stages(receipt)["computed_stages"]
        self.assertEqual(stages["CRAFT_REVIEWED"], "FAIL")
        self.assertEqual(stages["IMPLEMENTATION_VERIFIED"], "PASS")
        self.assertEqual(stages["EXECUTION_VERIFIED"], "PASS")

    def test_scenario_hash_staleness_is_attributed_to_execution(self):
        matrix = self.project / self.receipt()["scenario_matrix"]["path"]
        record = json.loads(matrix.read_text(encoding="utf-8-sig"))
        record["scenarios"][0]["id"] = "renamed-scenario"
        matrix.write_text(json.dumps(record, indent=2), encoding="utf-8")
        receipt = self.receipt()
        receipt["scenario_matrix"]["sha256"] = sha256_of(matrix)
        stages = self.stages(receipt)["computed_stages"]
        self.assertEqual(stages["EXECUTION_VERIFIED"], "FAIL")
        self.assertEqual(stages["SOURCE_VERIFIED"], "PASS")

    def test_run_artifact_outside_the_project_is_refused(self):
        outside = self.base / "leak.png"
        outside.write_bytes(b"x")

        def mutate(run):
            run["scenarios"][0].setdefault("artifacts", []).append(
                {"kind": "screenshot", "path": str(outside), "sha256": sha256_of(outside)})

        receipt = self.rechain("scenario_run", mutate)
        result = self.stages(receipt)
        self.assertEqual(result["computed_stages"]["EXECUTION_VERIFIED"], "FAIL")
        self.assertTrue(any(i.startswith("LOBSTER_RUNTIME_ARTIFACT_ESCAPES") for i in result["issues"]),
                        result["issues"][:4])

    def test_run_artifact_not_claimed_by_the_evidence_manifest_is_reported(self):
        stray = self.project / "artifacts" / "stray.png"
        stray.write_bytes(b"x")

        def mutate(run):
            run["scenarios"][0].setdefault("artifacts", []).append(
                {"kind": "screenshot", "path": "artifacts/stray.png", "sha256": sha256_of(stray)})

        receipt = self.rechain("scenario_run", mutate)
        result = self.stages(receipt)
        self.assertTrue(any(i.startswith("LOBSTER_RUNTIME_ARTIFACT_UNCLAIMED") for i in result["issues"]),
                        result["issues"][:4])


class GoldenRootPortabilityTests(unittest.TestCase):
    """The golden delivery must verify identically from any root and any cwd."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.addCleanup(os.chdir, Path.cwd())

    def verify_at(self, project, cwd):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", str(Path(project) / "receipt-final.json"),
             "--project", str(project)], capture_output=True, text=True, cwd=str(cwd))
        return json.loads(result.stdout), result.returncode

    def test_golden_is_identical_across_roots_and_cwds(self):
        roots = []
        for name in ("copy-a", "nested/deep/copy-b", "with space/copy c", "área/cópia"):
            target = self.base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(GOLDEN, target)
            roots.append(target)
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()

        seen = []
        for root in roots:
            for cwd in (self.base, elsewhere, root):
                payload, code = self.verify_at(root, cwd)
                seen.append((payload["status"], code, tuple(sorted(payload["computed_stages"].items())),
                             len(payload["issues"])))
        self.assertEqual(len(set(seen)), 1, f"golden is not root-portable: {set(seen)}")
        self.assertEqual(seen[0][0], "DELIVERY_READY")
        self.assertEqual(seen[0][1], 0)

    def test_golden_verifies_with_a_relative_project_from_its_parent(self):
        target = self.base / "project"
        shutil.copytree(GOLDEN, target)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-v3", "project/receipt-final.json", "--project", "project"],
            capture_output=True, text=True, cwd=str(self.base))
        self.assertEqual(json.loads(result.stdout)["status"], "DELIVERY_READY", result.stdout[:300])

    def test_golden_carries_no_unreferenced_scenario_matrix(self):
        """The duplicate at the golden root disagreed with the referenced one."""
        receipt = json.loads((GOLDEN / "receipt-final.json").read_text(encoding="utf-8-sig"))
        referenced = {value["path"] for value in receipt.values()
                      if isinstance(value, dict) and "path" in value}
        for stray in GOLDEN.glob("*matrix*.json"):
            self.assertIn(stray.relative_to(GOLDEN).as_posix(), referenced,
                          f"{stray.name} is not referenced by the receipt")

    def test_golden_records_every_path_relative_to_the_project_root(self):
        receipt = json.loads((GOLDEN / "receipt-final.json").read_text(encoding="utf-8-sig"))
        for field in ("scenario_matrix", "scenario_run", "evidence_manifest", "dependency_graph"):
            record = json.loads((GOLDEN / receipt[field]["path"]).read_text(encoding="utf-8-sig"))
            for raw in self.collect_paths(record):
                self.assertIsNotNone(lobster.contained_path(GOLDEN.resolve(), raw),
                                     f"{field} records {raw!r}, which is not project-relative")

    @staticmethod
    def collect_paths(record):
        found = []
        stack = [record]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "path" and isinstance(value, str):
                        found.append(value)
                    else:
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)
        return found


class CrossPlatformContainmentTests(unittest.TestCase):
    """I10: the containment decision is identical under POSIX and Windows rules.

    A real Linux kernel is not available in this environment, so this proves the
    platform-dependent half — how a spelling is CLASSIFIED — by executing the
    decision against both pathlib flavours and both node:path implementations.
    The filesystem half (resolve/is_relative_to) is flavour-independent pathlib.
    """

    REFUSED = [
        "/etc/passwd", "/", "//server/share/x", "\\\\server\\share\\x", "\\OUTSIDE\\secret",
        "C:/Windows/system32", "C:\\Windows", "c:x.txt", "../outside", "a/../../outside",
        "a\\..\\..\\outside", "..", "sub/../../..", "   ", "",
    ]
    ACCEPTED = [
        "index.html", "src/app.tsx", "artifacts/final/mobile.png", "a/b/c/d/e/f.txt",
        "foo bar/baz.css", "área/cópia.json", ".hidden/file", "a.b/c..d/e.txt",
        "src\\app.tsx", "artifacts\\final\\mobile.png",
    ]

    def test_python_decision_is_flavour_independent(self):
        for raw in self.REFUSED:
            with self.subTest(refused=raw):
                self.assertTrue(lobster.not_relative(raw.strip()) or not raw.strip(),
                                f"{raw!r} must be refused")
        for raw in self.ACCEPTED:
            with self.subTest(accepted=raw):
                self.assertFalse(lobster.not_relative(raw), f"{raw!r} must be accepted")

    def test_python_decision_matches_both_pure_flavours(self):
        """Every refused spelling is refused whichever flavour interprets it."""
        for raw in self.REFUSED:
            if not raw.strip():
                continue
            with self.subTest(raw=raw):
                posix_abs = PurePosixPath(raw).is_absolute()
                windows_abs = PureWindowsPath(raw).is_absolute()
                traversal = ".." in __import__("re").split(r"[\\/]", raw)
                drive = bool(__import__("re").match(r"^[a-zA-Z]:", raw))
                self.assertTrue(posix_abs or windows_abs or traversal or drive
                                or raw.startswith(("/", "\\")),
                                f"{raw!r} is in REFUSED but no rule explains why")
                self.assertTrue(lobster.not_relative(raw))

    def test_node_decision_agrees_with_python_under_posix_and_win32_rules(self):
        script = PACKAGE / "scripts" / "lib" / "contain.mjs"
        payload = json.dumps({"refused": self.REFUSED, "accepted": self.ACCEPTED})
        program = f"""
import {{ contain, notRelative }} from {json.dumps(script.as_uri())};
import nodePath from "node:path";
const cases = {payload};
const out = {{}};
for (const [impl, name] of [[nodePath.posix, "posix"], [nodePath.win32, "win32"]]) {{
  const root = name === "posix" ? "/project" : "C:\\\\project";
  out[name] = {{
    refused: cases.refused.map(r => contain(root, r, impl).path === null),
    accepted: cases.accepted.map(r => contain(root, r, impl).path !== null),
  }};
}}
out.notRelative = cases.refused.map(r => notRelative(r));
console.log(JSON.stringify(out));
"""
        result = subprocess.run(["node", "--input-type=module", "-e", program],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        for flavour in ("posix", "win32"):
            self.assertTrue(all(data[flavour]["refused"]),
                            f"{flavour}: accepted a path it must refuse: "
                            f"{[r for r, ok in zip(self.REFUSED, data[flavour]['refused']) if not ok]}")
            self.assertTrue(all(data[flavour]["accepted"]),
                            f"{flavour}: refused a legitimate path: "
                            f"{[r for r, ok in zip(self.ACCEPTED, data[flavour]['accepted']) if not ok]}")
        # and the Node decision equals the Python decision, spelling for spelling
        self.assertEqual(data["notRelative"], [lobster.not_relative(r) or not r.strip()
                                               for r in self.REFUSED])

    def test_posix_root_semantics_are_exercised_with_pure_posix_paths(self):
        """Containment arithmetic itself, done with POSIX separators end to end."""
        root = PurePosixPath("/srv/project")
        for raw, expected_inside in (("src/app.tsx", True), ("a/b/c.txt", True),
                                     ("../escape", False), ("/etc/passwd", False),
                                     ("a/../../escape", False), ("área/x", True)):
            with self.subTest(raw=raw):
                if lobster.not_relative(raw):
                    self.assertFalse(expected_inside, f"{raw!r} refused by spelling")
                    continue
                candidate = root / raw
                normalised = PurePosixPath(os.path.normpath(str(candidate)).replace("\\", "/"))
                self.assertEqual(normalised.is_relative_to(root), expected_inside, raw)


if __name__ == "__main__":
    unittest.main()
