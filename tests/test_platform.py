import copy
import json
import subprocess
import sys
import unittest

import test_lobster

SCRIPT = test_lobster.SCRIPT
lobster = test_lobster.lobster


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_lobster.V2Tests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.receipt = self.fixture.receipt
        self.record = {
            "schema": "lobster-platform/v1", "checked_at": "2026-09-07", "target_browsers": ["Synthetic browser 1"],
            "decisions": [{"capability": "fixture same-document transition", "choice": "native",
                           **{key: "Synthetic observed comparison" for key in "native_option library_option reason support_observation feature_detection fallback accessibility cost_comparison".split()},
                           "support_urls": ["https://example.org/fixture-support"], "support_evidence": self.fixture.source,
                           "implementation": self.fixture.owner, "evidence_ids": ["visual"], "fallback_evidence_ids": ["interaction"]}]}
        self.sync()

    def sync(self):
        self.receipt["platform_scout"] = self.fixture.file("platform.json", json.dumps(self.record))

    def test_native_hybrid_and_justified_library_choices_pass(self):
        for choice in ("native", "hybrid", "library"):
            self.record["decisions"][0]["choice"] = choice
            self.sync()
            self.assertEqual(lobster.verify(self.receipt, self.root, True)["status"], "READY_FOR_REVIEW")

    def test_required_scout_cannot_be_omitted_but_old_v2_is_readable(self):
        del self.receipt["platform_scout"]
        self.assertEqual(lobster.verify(self.receipt, self.root)["status"], "READY_FOR_REVIEW")
        self.assertEqual(lobster.verify(self.receipt, self.root, True)["status"], "INCOMPLETE")

    def test_attached_scout_is_checked_without_flag(self):
        self.record["decisions"][0]["reason"] = ""
        self.sync()
        self.assertEqual(lobster.verify(self.receipt, self.root)["status"], "INCOMPLETE")

    def test_fallback_plan_or_still_frame_is_not_exercised_fallback(self):
        for identity in ("visual", "missing", "check"):
            self.record["decisions"][0]["fallback_evidence_ids"] = [identity]
            self.sync()
            self.assertEqual(lobster.platform_check(self.receipt, self.root)["status"], "INCOMPLETE")

    def test_changed_owner_and_support_invalidate_scout(self):
        for reference in (self.fixture.owner, self.fixture.source):
            path = self.root / reference["path"]
            before = path.read_bytes()
            path.write_bytes(b"changed")
            self.assertEqual(lobster.platform_check(self.receipt, self.root)["status"], "INCOMPLETE")
            path.write_bytes(before)

    def test_malformed_scout_fields_return_findings(self):
        for field, value in (("decisions", None), ("decisions", [None]), ("target_browsers", []), ("checked_at", "yesterday"), ("checked_at", None), ("schema", "unknown")):
            original = copy.deepcopy(self.record)
            self.record[field] = value
            self.sync()
            self.assertEqual(lobster.platform_check(self.receipt, self.root)["status"], "INCOMPLETE")
            self.record = original

    def test_cli_requires_platform_when_requested(self):
        self.receipt.pop("platform_scout")
        path = self.root / "receipt.json"
        path.write_text(json.dumps(self.receipt), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "verify", str(path), "--project", str(self.root), "--require-platform"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("platform_scout", result.stdout)


if __name__ == "__main__":
    unittest.main()
