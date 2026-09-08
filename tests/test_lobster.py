"""Record integrity and real sibling-engine integration tests, not aesthetic evals."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lobster.py"
spec = importlib.util.spec_from_file_location("lobster", SCRIPT)
lobster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lobster)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.owner = self.file("src/component.tsx", "export const Component = () => null")
        self.usage = self.file("src/page.tsx", "import {Component} from './component'; export default Component")
        self.artifact = self.file("evidence/observação.txt", "Synthetic test evidence, not a real UI review.")
        self.source = self.file("evidence/source.txt", "Fixture license/revision observation")
        self.receipt = {
            "format": "lobster-receipt/v1", "surface": "fixture", "route": "/fixture", "limitations": [],
            "concepts": [{"id": "comparison", "law": "aligned labels", "product_reason": "scan adjacent records",
                          "implementation": self.owner, "evidence_ids": ["visual"]}],
            "components": [{"id": "fixture", "origin": "native", "mechanism": "record selection",
                            "implementation": self.owner, "usage": self.usage,
                            "evidence_ids": ["visual", "interaction"]}],
            "evidence": [{"id": kind, "kind": kind, "status": "passed", "target": "/fixture",
                          "observation": "Synthetic observation", "artifact": self.artifact,
                          "subject_files": [self.owner, self.usage],
                          **({"viewport": [390, 844], "state": "populated"} if kind == "visual" else {})}
                         for kind in ("visual", "interaction", "check")],
        }

    def file(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def verify(self):
        return lobster.verify(self.receipt, self.root)

    def test_complete_record_is_only_ready_for_review(self):
        result = self.verify()
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertIn("not UI execution", result["scope"])

    def test_changed_source_invalidates_old_render_and_interaction(self):
        (self.root / self.owner["path"]).write_text("changed", encoding="utf-8")
        self.assertIn("changed file", " ".join(self.verify()["issues"]))

    def test_evidence_must_cover_usage_not_only_component(self):
        for evidence in self.receipt["evidence"]:
            evidence["subject_files"] = [self.owner]
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_missing_artifact_is_rejected(self):
        (self.root / self.artifact["path"]).unlink()
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_missing_browser_is_honest_incomplete(self):
        visual = self.receipt["evidence"][0]
        visual.update(status="unverified", reason="No browser capability")
        visual.pop("artifact")
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_install_without_external_source_record_fails(self):
        self.receipt["components"][0]["origin"] = "external"
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_external_record_requires_revision_license_and_source(self):
        component = self.receipt["components"][0]
        component.update(origin="external", source_url="https://example.org/fixture", revision="fixture-1",
                         license="MIT", source_evidence=self.source)
        self.assertEqual(self.verify()["status"], "READY_FOR_REVIEW")
        component["revision"] = "UNVERIFIED"
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_custom_fallback_requires_reason(self):
        component = self.receipt["components"][0]
        component["origin"] = "custom"
        self.assertEqual(self.verify()["status"], "INCOMPLETE")
        component["reason"] = "Existing choices violate required behavior"
        self.assertEqual(self.verify()["status"], "READY_FOR_REVIEW")

    def test_path_escape_and_absolute_paths_are_rejected(self):
        for path in ("../secret", "..\\secret", "C:\\secret", "/secret"):
            with self.subTest(path=path):
                self.receipt["concepts"][0]["implementation"] = {"path": path, "sha256": "a" * 64}
                self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_duplicate_ids_and_unknown_proof_rejected(self):
        self.receipt["evidence"].append(copy.deepcopy(self.receipt["evidence"][0]))
        self.receipt["concepts"][0]["evidence_ids"] = ["made-up"]
        errors = " ".join(self.verify()["issues"])
        self.assertIn("duplicate", errors)
        self.assertIn("unknown evidence", errors)

    def test_malformed_rows_are_findings_not_crashes(self):
        self.receipt["concepts"] = [None, {"id": []}]
        self.receipt["components"] = None
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_failed_check_blocks_readiness(self):
        self.receipt["evidence"][-1]["status"] = "failed"
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_cli_missing_input_returns_inspection_error(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "verify", str(self.root / "absent.json"),
                                 "--project", str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "ERROR")


class DiscoveryTests(unittest.TestCase):
    @unittest.skipUnless((lobster.BUILTIN / "plief-sifr/scripts/query_design_concepts.py").is_file() and
                         (lobster.BUILTIN / "plief-orun/scripts/query_capabilities.py").is_file(),
                         "Separate Sifr/Orun sibling packages are not present")
    def test_actual_sifr_and_orun_queries(self):
        result = lobster.discover("editorial archive typography reading", "accessible command menu keyboard search", "React")
        self.assertEqual(result["results"]["sifr"]["status"], "OK")
        self.assertEqual(result["results"]["orun"]["status"], "OK")
        self.assertFalse(result["installation_performed"])
        self.assertFalse(result["native_inspection_performed"])
        self.assertLessEqual(len(result["results"]["sifr"]["data"]["matches"]), 4)
        self.assertLessEqual(len(result["results"]["orun"]["data"]["candidates"]), 4)

    def test_absent_engine_is_error_not_no_match(self):
        self.assertEqual(lobster.query(Path("missing-engine.py"), "x", [], "matches")["status"], "ERROR")

    def test_zero_matches_remain_distinct_from_error(self):
        fake = subprocess.CompletedProcess([], 0, '{"matches": []}', '')
        with patch.object(lobster.subprocess, "run", return_value=fake):
            self.assertEqual(lobster.query(SCRIPT, "x", [], "matches")["status"], "NO_MATCH")

    def test_engine_bad_json_is_error(self):
        fake = subprocess.CompletedProcess([], 0, 'not-json', '')
        with patch.object(lobster.subprocess, "run", return_value=fake):
            self.assertEqual(lobster.query(SCRIPT, "x", [], "matches")["status"], "ERROR")

    def test_standalone_discovery_reports_optional_engine_unavailable(self):
        with patch.dict("os.environ", {"PLIEF_SIFR_PATH": str(Path(tempfile.gettempdir()) / "lobster-missing-sifr")}, clear=False):
            result = lobster.discover("archive concept", None)
        self.assertEqual(result["results"]["sifr"]["status"], "UNAVAILABLE")
        self.assertIn("could not be resolved", result["results"]["sifr"]["reason"])

    def test_doctor_is_ready_without_optional_integrations(self):
        result = lobster.doctor()
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["integrations"]["sifr"]["required"], False)


class V2Tests(ReceiptTests):
    def setUp(self):
        super().setUp()
        self.research_record = {
            "schema": "lobster-research/v1", "need": "fixture spatial navigation", "queries": ["fixture accessible spatial navigation"],
            "sources": [{"name": name, "url": f"https://example.org/{name}", "category": categories,
                         "mode": "BOTH", "access": "official", "inspected": True,
                         "observation": "Synthetic observed mechanism", "evidence": self.source}
                        for name, categories in (("structural", ["PRIMITIVE"]), ("expressive", ["SHADER", "MOTION"]), ("reference", ["DESIGN_SYSTEM"]))],
            "candidates": [{"name": name, "source": name, "url": f"https://example.org/{name}/item",
                            "mechanism": "spatial alignment", "interaction_mechanism": "keyboard selection", "framework": "React",
                            "stack_fit": "fixture compatible", "license": "MIT", "dependencies": [], "bundle_implications": "0 additional bytes",
                            "accessibility": "fixture keyboard observation", "adaptation_cost": "one wrapper", "status": "reference" if name == "reference" else "rejected",
                            "reason": "reference informs alignment" if name == "reference" else "native is sufficient"}
                           for name in ("structural", "expressive", "reference")],
            "implementation_impacts": [{"candidate": "reference", "change": "align selection labels", "implementation": self.owner, "evidence_ids": ["visual"]}],
        }
        self.receipt.update(format="lobster-receipt/v2",
                            profile={"substantial": True, "expressive": True, "motion": True, "3d": True, "heavy_effects": True},
                            craft_contract={key: "Synthetic fixture decision" for key in lobster.CRAFT_FIELDS},
                            craft_scorecard=[{"dimension": key, "score": 4, "central": True, "observation": "Synthetic review", "evidence_ids": ["visual"]}
                                             for key in lobster.CRAFT_DIMENSIONS + lobster.SCENE_DIMENSIONS],
                            craft_gates={key: {"status": "passed", "observation": "Synthetic exercised gate", "evidence_ids": ["check", "visual", "interaction"]}
                                         for key in ("implementation", "integration", "visual", "motion", "3d")},
                            motion_evidence=[{**{key: "Synthetic temporal observation" for key in "trigger from to duration_easing interruption reduced_motion".split()}, "evidence_ids": ["interaction"]}],
                            **{"3d_evidence": [{**{key: "Synthetic scene observation" for key in "asset_source model_format texture_sizes renderer_dpr lighting camera performance_observation mobile_fallback".split()}, "evidence_ids": ["visual", "interaction"]}]},
                            performance_budget={**{key: "Synthetic measured budget" for key in "js_cost asset_weight texture_memory video draw_calls animation_work layout_work measured_result fallback".split()}, "evidence_ids": ["check"]})
        self.sync_research()

    def sync_research(self):
        self.receipt["research"] = {"required": True, "artifact": self.file("research.json", json.dumps(self.research_record)),
                                    "sources_consulted": [row["name"] for row in self.research_record["sources"]],
                                    "selected_references": [row["name"] for row in self.research_record["candidates"] if row["status"] in ("selected", "reference")],
                                    "impact": [row["change"] for row in self.research_record["implementation_impacts"]]}

    def test_draft_is_not_research(self):
        draft = lobster.research("fixture hero", "React", "components,motion,3d")
        self.assertFalse(draft["research_performed"])
        self.assertEqual(lobster.research_verify(draft, self.root)["status"], "INCOMPLETE")

    def test_missing_impact_catches_component_amnesia(self):
        self.research_record["implementation_impacts"] = []
        self.sync_research()
        self.assertIn("cannot disappear", " ".join(self.verify()["issues"]))

    def test_filled_draft_must_not_claim_research_was_unperformed(self):
        self.research_record["research_performed"] = False
        self.assertEqual(lobster.research_verify(self.research_record, self.root)["status"], "INCOMPLETE")

    def test_selected_acquisition_requires_reachable_external_receipt(self):
        self.research_record["candidates"][-1]["status"] = "selected"
        self.sync_research()
        self.assertIn("integrated external", " ".join(self.verify()["issues"]))
        self.receipt["components"][0].update(origin="external", source_url="https://example.org/reference/item", license="MIT", revision="fixture-1", source_evidence=self.source)
        self.assertEqual(self.verify()["status"], "READY_FOR_REVIEW")

    def test_reference_only_cannot_be_acquired(self):
        self.research_record["sources"][-1]["mode"] = "REFERENCE_ONLY"
        self.research_record["candidates"][-1]["status"] = "selected"
        self.sync_research()
        self.assertIn("reference-only", " ".join(self.verify()["issues"]))

    def test_research_breadth_and_diversity_are_separate(self):
        for row in self.research_record["sources"]:
            row["category"] = ["COMPONENT"]
        self.assertEqual(lobster.research_verify(self.research_record, self.root)["status"], "READY_FOR_REVIEW")
        self.assertEqual(lobster.research_verify(self.research_record, self.root, True)["status"], "INCOMPLETE")
        for row in self.research_record["sources"]:
            row["url"] = "https://example.org/same"
        self.assertIn("3 distinct", " ".join(lobster.research_verify(self.research_record, self.root)["issues"]))

    def test_research_summary_must_match_artifact(self):
        self.receipt["research"]["impact"] = ["invented"]
        self.assertIn("differs", " ".join(self.verify()["issues"]))

    def test_research_cannot_be_waived(self):
        self.receipt["research"] = {"required": False, "reason": "prefer to skip"}
        self.assertIn("cannot be waived", " ".join(self.verify()["issues"]))

    def test_research_impact_needs_owner_and_known_evidence(self):
        for identity in ("missing", "check"):
            self.research_record["implementation_impacts"][0]["evidence_ids"] = [identity]
            self.sync_research()
            self.assertIn("owner proof", " ".join(self.verify()["issues"]))

    def test_central_low_score_cannot_be_averaged_away(self):
        self.receipt["craft_scorecard"][0]["score"] = 2
        self.assertIn("requires repair", " ".join(self.verify()["issues"]))

    def test_boolean_is_not_numeric_score(self):
        self.receipt["craft_scorecard"][0]["score"] = True
        self.assertIn("integer 1..5", " ".join(self.verify()["issues"]))

    def test_motion_still_frame_does_not_pass_temporal_gate(self):
        self.receipt["motion_evidence"][0]["evidence_ids"] = ["visual"]
        self.assertEqual(self.verify()["status"], "INCOMPLETE")

    def test_missing_scene_and_budget_observations_block(self):
        self.receipt["3d_evidence"][0].pop("renderer_dpr")
        self.receipt["performance_budget"].pop("measured_result")
        errors = " ".join(self.verify()["issues"])
        self.assertIn("renderer_dpr", errors)
        self.assertIn("measured_result", errors)

    def test_changed_research_artifact_invalidates_receipt(self):
        (self.root / "research.json").write_text("{}")
        self.assertIn("changed file research.json", " ".join(self.verify()["issues"]))

    def test_malformed_extensions_are_findings(self):
        for key in ("profile", "research", "craft_contract", "craft_scorecard", "craft_gates", "motion_evidence", "3d_evidence", "performance_budget"):
            for value in (None, [], "bad", 12):
                with self.subTest(key=key, value=value):
                    receipt = copy.deepcopy(self.receipt)
                    receipt[key] = value
                    self.assertEqual(lobster.verify(receipt, self.root)["status"], "INCOMPLETE")

    def test_research_malformed_rows_are_findings(self):
        for key in ("sources", "candidates", "implementation_impacts"):
            for value in (None, [None], [{"name": []}], "bad"):
                with self.subTest(key=key, value=value):
                    record = copy.deepcopy(self.research_record)
                    record[key] = value
                    self.assertEqual(lobster.research_verify(record, self.root)["status"], "INCOMPLETE")

    def test_research_rejects_unsafe_paths_and_credential_urls(self):
        for path in ("../outside", "..\\outside", "/outside", "C:\\outside"):
            self.research_record["sources"][0]["evidence"] = {"path": path, "sha256": "a" * 64}
            self.assertEqual(lobster.research_verify(self.research_record, self.root)["status"], "INCOMPLETE")
        self.research_record["sources"][0]["url"] = "https://user:fixture@example.org"
        self.assertIn("without credentials", " ".join(lobster.research_verify(self.research_record, self.root)["issues"]))

    def test_cli_new_commands_and_no_overwrite(self):
        draft = self.root / "draft.json"
        command = [sys.executable, str(SCRIPT), "research", "--need", "fixture", "--out", str(draft)]
        created = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        duplicate = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(duplicate.returncode, 2)
        path = self.root / "receipt.json"
        path.write_text(json.dumps(self.receipt), encoding="utf-8")
        for name, input_path in (("research-verify", self.root / "research.json"), ("craft-check", path), ("verify", path)):
            result = subprocess.run([sys.executable, str(SCRIPT), name, str(input_path), "--project", str(self.root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        invalid = subprocess.run([sys.executable, str(SCRIPT), "research-verify", str(draft), "--project", str(self.root)], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 1)


if __name__ == "__main__":
    unittest.main()
