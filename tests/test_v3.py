import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_lobster


class V3Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "src").mkdir()
        (self.root / "src/app.tsx").write_text("export default function App() { return null }", encoding="utf-8")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(test_lobster.SCRIPT), *args], capture_output=True, text=True)

    def test_auto_profile_does_not_trust_receipt_flags(self):
        result = test_lobster.lobster.auto_profile(self.root, "premium responsive landing with animation")
        self.assertTrue(result["signals"]["substantial"])
        self.assertIn("browser_execution", result["required_gates"])

    def test_plan_routes_only_relevant_domains(self):
        result = test_lobster.lobster.plan(self.root, "settings form")
        self.assertIn("form_craft", result["required"])
        self.assertNotIn("3d", result["required"])

    def test_runtime_adapter_is_honest_when_playwright_missing(self):
        output = self.root / "runtime.json"
        result = subprocess.run(["node", str(Path(test_lobster.SCRIPT).parent / "browser-runner.mjs"), str(output), "http://127.0.0.1:9"], capture_output=True, text=True)
        if result.returncode == 1:
            self.assertEqual(json.loads(output.read_text())["status"], "UNAVAILABLE")
        else:
            self.assertIn(result.returncode, (0, 1))

    def test_v3_stages_are_monotonic(self):
        good = {"format":"lobster-receipt/v3","surface":"x","revision":"r","stages":{stage:"PASS" for stage in test_lobster.lobster.V3_STAGES}}
        for field in ("profile","research","platform_scout","provenance_lock","dependency_graph","scenario_run","craft_review","repair_ledger","verdict"):
            path = self.root / f"{field}.json"; path.write_text("{}", encoding="utf-8"); good[field] = {"path":path.name,"sha256":__import__('hashlib').sha256(path.read_bytes()).hexdigest()}
        self.assertEqual(test_lobster.lobster.v3_verify(good, self.root)["status"], "INCOMPLETE")
        self.assertIn("LOBSTER_SCHEMA_REQUIRED_FIELD", " ".join(test_lobster.lobster.v3_verify(good, self.root)["issues"]))

    def test_agent_stage_claim_cannot_upgrade_empty_artifacts(self):
        good = {"format":"lobster-receipt/v3","surface":"x","revision":"r","stages":{stage:"PASS" for stage in test_lobster.lobster.V3_STAGES}}
        for field in ("profile","research","platform_scout","provenance_lock","dependency_graph","scenario_run","craft_review","repair_ledger"):
            path = self.root / f"{field}.json"; path.write_text("{}", encoding="utf-8"); good[field] = {"path":path.name,"sha256":__import__('hashlib').sha256(path.read_bytes()).hexdigest()}
        result = test_lobster.lobster.v3_verify(good, self.root)
        self.assertEqual(result["computed_verdict"], "INCOMPLETE")
        self.assertNotIn("DELIVERY_READY", result["computed_stages"])

    def test_v3_ignores_fake_verdict_pointer(self):
        path = self.root / "verdict.json"; path.write_text(json.dumps({"schema":"lobster-verdict/v1","status":"DELIVERY_READY","stages":{}}), encoding="utf-8")
        receipt = {"format":"lobster-receipt/v3","surface":"x","revision":"r","verdict":{"path":path.name,"sha256":__import__('hashlib').sha256(path.read_bytes()).hexdigest()}}
        result = test_lobster.lobster.v3_verify(receipt, self.root)
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_cross_artifact_hash_mismatch_blocks_execution(self):
        run = self.root / "run.json"
        matrix = self.root / "matrix.json"
        run.write_text(json.dumps({"schema": "lobster-runtime/v2", "status": "PASS", "scenario_hash": "wrong", "project_fingerprint": "p", "dependency_fingerprint": "d", "scenarios": []}), encoding="utf-8")
        matrix.write_text(json.dumps({"schema": "lobster-scenario-matrix/v1", "scenarios": [{"id": "smoke", "viewport": {"width": 800, "height": 600}, "steps": [{"action": "goto", "url": "/"}], "assertions": [{"assert": "url", "value": "http://example.test/"}]}]}), encoding="utf-8")
        receipt = {"format": "lobster-receipt/v3", "surface": "x", "revision": "r", "scenario_matrix": {"path": matrix.name, "sha256": __import__('hashlib').sha256(matrix.read_bytes()).hexdigest()}, "scenario_run": {"path": run.name, "sha256": __import__('hashlib').sha256(run.read_bytes()).hexdigest()}}
        result = test_lobster.lobster.v3_verify(receipt, self.root)
        self.assertEqual(result["computed_verdict"], "INCOMPLETE")
        self.assertTrue(any("SCENARIO_HASH" in issue for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
