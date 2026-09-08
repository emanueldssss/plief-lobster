#!/usr/bin/env python3
"""Local Sifr/Orun retrieval and delivery-record integrity. Python stdlib only.

No installation, network requests, UI execution, or aesthetic certification.
Exit: 0 usable/ready for review, 1 incomplete/no matches, 2 inspection error.
"""
from __future__ import annotations

import argparse
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

BUILTIN = Path(__file__).resolve().parents[2]
SHA256 = re.compile(r"[0-9a-f]{64}", re.IGNORECASE)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def query(script: Path, query_text: str, options: list[str], key: str) -> dict:
    if not script.is_file():
        return {"status": "ERROR", "reason": f"Missing sibling engine: {script}"}
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(script), query_text, *options, "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
        )
        if result.returncode:
            return {"status": "ERROR", "reason": result.stderr[-1500:] or result.stdout[-1500:]}
        data = json.loads(result.stdout)
        if not isinstance(data, dict) or not isinstance(data.get(key), list):
            return {"status": "ERROR", "reason": f"Engine response missing {key} array"}
        return {"status": "OK" if data[key] else "NO_MATCH", "data": data}
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return {"status": "ERROR", "reason": str(exc)}


def discover(concept: str | None, capability: str | None, framework: str = "") -> dict:
    jobs = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        if concept:
            jobs["sifr"] = pool.submit(query, BUILTIN / "plief-sifr/scripts/query_design_concepts.py",
                                       concept, ["--top-k", "4"], "matches")
        if capability:
            options = ["--top-k", "4"] + (["--framework", framework] if framework else [])
            jobs["orun"] = pool.submit(query, BUILTIN / "plief-orun/scripts/query_capabilities.py",
                                       capability, options, "candidates")
        return {"format": "lobster-discovery/v1", "authority": "LOCAL_INDEX_ONLY",
                "native_inspection_performed": False, "installation_performed": False,
                "results": {name: future.result() for name, future in jobs.items()}}


def verify_implementation(receipt, project: Path) -> dict:
    root = project.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project must be a directory")
    issues: list[str] = []

    def require(condition, message):
        if not condition:
            issues.append(message)
        return bool(condition)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def file_ref(value, label):
        if not isinstance(value, dict):
            issues.append(f"{label}: expected path/sha256 object")
            return None
        raw, digest = value.get("path"), value.get("sha256")
        if not text(raw) or not isinstance(digest, str) or not SHA256.fullmatch(digest):
            issues.append(f"{label}: nonempty path and SHA-256 required")
            return None
        relative = Path(raw)
        # Reject both Windows and POSIX absolute/traversal forms on either host.
        if relative.is_absolute() or re.match(r"^[a-zA-Z]:", raw) or raw.startswith(("\\", "/")) or ".." in raw.replace("\\", "/").split("/"):
            issues.append(f"{label}: path must stay project-relative")
            return None
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            issues.append(f"{label}: resolved path escapes project")
            return None
        if not path.is_file():
            issues.append(f"{label}: missing file {raw}")
            return None
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            issues.append(f"{label}: cannot read {raw}: {exc}")
            return None
        if not require(actual == digest.lower(), f"{label}: changed file {raw}; refresh evidence after verification"):
            return None
        return path

    def rows(key):
        value = receipt.get(key)
        if not isinstance(value, list) or not value:
            issues.append(f"{key}: nonempty array required")
            return []
        seen = set()
        valid = []
        for row in value:
            if not isinstance(row, dict) or not text(row.get("id")):
                issues.append(f"{key}: each row requires a nonempty id")
                continue
            require(row["id"] not in seen, f"{key}: duplicate id {row['id']}")
            seen.add(row["id"])
            valid.append(row)
        return valid

    if not isinstance(receipt, dict):
        return {"status": "INCOMPLETE", "issues": ["receipt must be an object"]}
    require(receipt.get("format") == "lobster-receipt/v1", "unsupported receipt format")
    for key in ("surface", "route"):
        require(text(receipt.get(key)), f"{key}: nonempty string required")
    require(isinstance(receipt.get("limitations"), list) and all(text(x) for x in receipt.get("limitations", [])),
            "limitations: array of nonempty strings required")

    evidence_by_id = {}
    kinds = set()
    for item in rows("evidence"):
        label = f"evidence:{item['id']}"
        kind, status = item.get("kind"), item.get("status")
        require(kind in ("visual", "interaction", "check"), f"{label}: invalid kind")
        if kind in ("visual", "interaction", "check"):
            kinds.add(kind)
        require(status in ("passed", "failed", "unverified"), f"{label}: invalid status")
        require(status == "passed", f"{label}: not passed ({status})")
        for field in ("target", "observation"):
            require(text(item.get(field)), f"{label}: {field} required")
        if status == "unverified":
            require(text(item.get("reason")), f"{label}: unverified reason required")
        else:
            file_ref(item.get("artifact"), f"{label}.artifact")
        subjects = item.get("subject_files")
        paths = set()
        if require(isinstance(subjects, list) and bool(subjects), f"{label}: subject_files required"):
            for subject in subjects:
                path = file_ref(subject, f"{label}.subject")
                if path is not None:
                    paths.add(path)
        if kind == "visual":
            viewport = item.get("viewport")
            require(isinstance(viewport, list) and len(viewport) == 2 and
                    all(type(n) is int and n > 0 for n in viewport), f"{label}: viewport must be [width, height]")
            require(text(item.get("state")), f"{label}: state required")
        evidence_by_id[item["id"]] = (kind, status, paths)
    require(kinds == {"visual", "interaction", "check"}, "visual, interaction and check evidence required")

    def proof(row, label, owner_paths, required_kinds):
        ids = row.get("evidence_ids")
        if not require(isinstance(ids, list) and bool(ids), f"{label}: evidence_ids required"):
            return
        covered = set()
        for eid in ids:
            if not isinstance(eid, str) or eid not in evidence_by_id:
                issues.append(f"{label}: unknown evidence id {eid!r}")
                continue
            kind, status, paths = evidence_by_id[eid]
            if status == "passed" and owner_paths and owner_paths.issubset(paths):
                covered.add(kind)
        require(required_kinds.issubset(covered), f"{label}: current owner files need {sorted(required_kinds)} proof")

    for row in rows("concepts"):
        label = f"concept:{row['id']}"
        for field in ("law", "product_reason"):
            require(text(row.get(field)), f"{label}: {field} required")
        owner = file_ref(row.get("implementation"), label)
        ids = row.get("evidence_ids", [])
        acceptable = {evidence_by_id[eid][0] for eid in ids if isinstance(eid, str) and eid in evidence_by_id} if isinstance(ids, list) else set()
        kind = "visual" if "visual" in acceptable else "interaction"
        proof(row, label, {owner} if owner else set(), {kind})

    for row in rows("components"):
        label = f"component:{row['id']}"
        origin = row.get("origin")
        require(origin in ("native", "external", "custom"), f"{label}: invalid origin")
        require(text(row.get("mechanism")), f"{label}: mechanism required")
        implementation = file_ref(row.get("implementation"), f"{label}.implementation")
        usage = file_ref(row.get("usage"), f"{label}.usage")
        if origin == "external":
            url = row.get("source_url", "")
            try:
                parsed = urlparse(url) if isinstance(url, str) else None
                valid_url = parsed and parsed.scheme in ("https", "http") and parsed.hostname and not parsed.username
            except ValueError:
                valid_url = False
            require(valid_url, f"{label}: official source URL required")
            for field in ("revision", "license"):
                require(text(row.get(field)) and row[field].upper() not in ("UNKNOWN", "UNVERIFIED", "STALE"),
                        f"{label}: inspected {field} required")
            file_ref(row.get("source_evidence"), f"{label}.source_evidence")
        if origin == "custom":
            require(text(row.get("reason")), f"{label}: custom implementation reason required")
        owners = {implementation, usage} if implementation and usage else set()
        proof(row, label, owners, {"visual", "interaction"})

    return {"status": "INCOMPLETE" if issues else "READY_FOR_REVIEW", "issues": issues,
            "scope": "Record and file integrity only; not UI execution, source authenticity or design certification."}


RESEARCH_SCHEMA = "lobster-research/v1"
CRAFT_DIMENSIONS = "composition typography spacing color material component_coherence motion interaction responsiveness accessibility performance specificity".split()
SCENE_DIMENSIONS = "geometry materials lighting camera rendering_fidelity 3d_performance".split()
CRAFT_FIELDS = "dominant_composition type_system spacing_rhythm surface_material_model motion_grammar corner_language icon_language image_3d_treatment scroll_behavior primary_expressive_mechanism effects_budget".split()
CATEGORIES = set("PRIMITIVE COMPONENT BLOCK MOTION SCROLL 3D SHADER TYPOGRAPHY TOKENS DESIGN_SYSTEM VISUAL_REFERENCE ASSET ICON DATA_VIS PATTERN MATERIAL LAYOUT".split())


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def web_url(value):
    try:
        parsed = urlparse(value) if isinstance(value, str) else None
        return bool(parsed and parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password)
    except ValueError:
        return False


class RecordCheck:
    def __init__(self, project):
        self.root = Path(project).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("project must be a directory")
        self.issues = []

    def require(self, condition, message):
        if not condition:
            self.issues.append(message)
        return bool(condition)

    def fields(self, row, names, label):
        for name in names:
            self.require(nonempty(row.get(name)), f"{label}: {name} required")

    def rows(self, value, label, required=True):
        if not self.require(isinstance(value, list), f"{label}: array required"):
            return []
        if required:
            self.require(bool(value), f"{label}: nonempty array required")
        result = []
        for row in value:
            if self.require(isinstance(row, dict), f"{label}: object entries required"):
                result.append(row)
        return result

    def strings(self, value, label, required=True):
        valid = isinstance(value, list) and all(nonempty(item) for item in value)
        if not self.require(valid and (bool(value) or not required), f"{label}: string array required"):
            return []
        self.require(len(value) == len(set(value)), f"{label}: duplicate entries")
        return value

    def file(self, value, label):
        if not self.require(isinstance(value, dict), f"{label}: path/sha256 required"):
            return None
        raw, digest = value.get("path"), value.get("sha256")
        if not self.require(nonempty(raw) and isinstance(digest, str) and SHA256.fullmatch(digest), f"{label}: invalid path/hash"):
            return None
        if not self.require(not raw.startswith(("/", "\\")) and not re.match(r"^[a-zA-Z]:", raw) and ".." not in raw.replace("\\", "/").split("/"), f"{label}: project-relative path required"):
            return None
        path = (self.root / raw).resolve()
        if not self.require(path.is_relative_to(self.root), f"{label}: path escapes project"):
            return None
        if not self.require(path.is_file(), f"{label}: missing file {raw}"):
            return None
        if not self.require(hashlib.sha256(path.read_bytes()).hexdigest() == digest.lower(), f"{label}: changed file {raw}"):
            return None
        return path

    def result(self):
        return {"status": "INCOMPLETE" if self.issues else "READY_FOR_REVIEW", "issues": self.issues,
                "scope": "Record and file integrity only; not UI execution, source authenticity or design certification."}


def research(need, framework, categories):
    if not nonempty(need):
        raise ValueError("need must be nonempty")
    normalized = [item.strip().upper() for item in categories.split(",") if item.strip()]
    normalized = [{"COMPONENTS": "COMPONENT", "PRIMITIVES": "PRIMITIVE"}.get(item, item) for item in normalized]
    if not normalized or any(item not in CATEGORIES for item in normalized):
        raise ValueError("categories must use the reference-fabric vocabulary")
    return {"schema": RESEARCH_SCHEMA, "need": need, "framework": framework, "categories": normalized,
            "research_performed": False, "queries": [], "sources": [], "candidates": [],
            "implementation_impacts": []}


def research_verify(record, project, expressive=False):
    check = RecordCheck(project)
    if not check.require(isinstance(record, dict), "research: object required"):
        return check.result()
    check.require(record.get("schema") == RESEARCH_SCHEMA, "research: unsupported schema")
    check.require(record.get("research_performed", True) is True, "research: draft still marked unperformed")
    check.fields(record, ["need"], "research")
    check.strings(record.get("queries"), "queries")
    sources = {}
    source_urls = set()
    categories = set()
    for row in check.rows(record.get("sources"), "sources"):
        check.fields(row, ["name", "observation"], "source")
        name = row.get("name")
        if not nonempty(name):
            continue
        check.require(name not in sources, f"source: duplicate {name}")
        check.require(web_url(row.get("url")), f"source:{name}: HTTP(S) URL without credentials required")
        check.require(row.get("access") in ("official", "community", "reference"), f"source:{name}: invalid access")
        check.require(row.get("mode") in ("ACQUISITION", "REFERENCE_ONLY", "BOTH"), f"source:{name}: invalid mode")
        source_categories = check.strings(row.get("category"), f"source:{name}.category")
        check.require(all(item in CATEGORIES for item in source_categories), f"source:{name}: invalid category")
        check.require(row.get("inspected") is True, f"source:{name}: inspection required")
        artifact = check.file(row.get("evidence"), f"source:{name}.evidence")
        sources[name] = row
        if row.get("inspected") is True and artifact and web_url(row.get("url")):
            source_urls.add(row["url"].rstrip("/"))
            categories.update(source_categories)
    check.require(len(source_urls) >= 3, "research: inspect at least 3 distinct relevant source URLs")
    if expressive:
        for label, choices in {"structural": {"PRIMITIVE", "COMPONENT", "BLOCK"}, "expressive": {"SHADER", "ASSET", "MATERIAL", "LAYOUT"}, "behavior/motion": {"MOTION", "SCROLL", "3D"}, "visual/design reference": {"VISUAL_REFERENCE", "DESIGN_SYSTEM"}}.items():
            check.require(bool(categories & choices), f"research: missing {label} source class")
    candidates = {}
    used_sources = set()
    for row in check.rows(record.get("candidates"), "candidates"):
        check.fields(row, "name source mechanism interaction_mechanism stack_fit framework license bundle_implications accessibility adaptation_cost reason".split(), "candidate")
        name, source = row.get("name"), row.get("source")
        if not nonempty(name) or not nonempty(source):
            continue
        check.require(name not in candidates, f"candidate: duplicate {name}")
        check.require(source in sources, f"candidate:{name}: unknown source")
        used_sources.add(source)
        check.require(web_url(row.get("url")), f"candidate:{name}: URL required")
        check.strings(row.get("dependencies"), f"candidate:{name}.dependencies", required=False)
        status = row.get("status")
        check.require(status in ("selected", "rejected", "reference"), f"candidate:{name}: explicit disposition required")
        if status == "selected":
            check.require(sources.get(source, {}).get("mode") != "REFERENCE_ONLY", f"candidate:{name}: reference-only source cannot prove acquisition")
            check.require(nonempty(row.get("license")) and row["license"].upper() not in ("UNKNOWN", "UNVERIFIED", "STALE", "N/A"), f"candidate:{name}: inspected license required for acquisition")
        candidates[name] = row
    check.require(set(sources).issubset(used_sources), "research: each counted source needs an inspected candidate and disposition")
    impacted = set()
    for row in check.rows(record.get("implementation_impacts"), "implementation_impacts"):
        name = row.get("candidate")
        if not nonempty(name):
            check.require(False, "impact: candidate required")
            continue
        candidate = candidates.get(name, {})
        check.require(candidate.get("status") in ("selected", "reference"), f"impact:{name}: active candidate required")
        check.fields(row, ["change"], f"impact:{name}")
        check.require(str(row.get("change", "")).strip().lower() not in ("nothing", "none", "n/a"), f"impact:{name}: concrete change required")
        check.file(row.get("implementation"), f"impact:{name}.implementation")
        check.strings(row.get("evidence_ids"), f"impact:{name}.evidence_ids")
        impacted.add(name)
    expected = {name for name, row in candidates.items() if row.get("status") in ("selected", "reference")}
    check.require(expected.issubset(impacted), "research: selected/reference candidates cannot disappear; record implementation impacts")
    return check.result()


def craft_check(receipt, project):
    check = RecordCheck(project)
    if not check.require(isinstance(receipt, dict), "receipt: object required"):
        return check.result()
    profile = receipt.get("profile")
    if not check.require(isinstance(profile, dict), "profile: object required"):
        return check.result()
    for name in ("substantial", "expressive", "motion", "3d", "heavy_effects"):
        check.require(type(profile.get(name)) is bool, f"profile:{name}: boolean required")
    contract = receipt.get("craft_contract")
    if check.require(isinstance(contract, dict), "craft_contract: object required"):
        check.fields(contract, CRAFT_FIELDS, "craft_contract")
    evidence = {}
    for row in check.rows(receipt.get("evidence"), "evidence"):
        if nonempty(row.get("id")):
            evidence[row["id"]] = row

    def proof(row, label, kinds=None):
        ids = check.strings(row.get("evidence_ids"), f"{label}.evidence_ids")
        covered = set()
        for identity in ids:
            item = evidence.get(identity, {})
            check.require(item.get("status") == "passed", f"{label}: missing/pending evidence {identity}")
            if isinstance(item.get("kind"), str):
                covered.add(item["kind"])
            check.file(item.get("artifact"), f"{label}:{identity}.artifact")
            for subject in check.rows(item.get("subject_files"), f"{label}:{identity}.subject_files"):
                check.file(subject, f"{label}:{identity}.subject")
        if kinds:
            check.require(set(kinds).issubset(covered), f"{label}: requires {sorted(kinds)} evidence")

    dimensions = set(CRAFT_DIMENSIONS + (SCENE_DIMENSIONS if profile.get("3d") else []))
    scores = {}
    for row in check.rows(receipt.get("craft_scorecard"), "craft_scorecard"):
        name = row.get("dimension")
        if not nonempty(name):
            check.require(False, "scorecard: dimension required")
            continue
        check.require(name not in scores, f"scorecard: duplicate {name}")
        scores[name] = row
        check.require(type(row.get("central")) is bool, f"scorecard:{name}: central boolean required")
        check.fields(row, ["observation"], f"scorecard:{name}")
        score = row.get("score")
        applicable = not (name == "motion" and not profile.get("motion"))
        if score is None and not applicable:
            check.fields(row, ["reason"], f"scorecard:{name}")
            continue
        if check.require(type(score) is int and 1 <= score <= 5, f"scorecard:{name}: integer 1..5 required"):
            check.require(not (row.get("central") and score <= 2), f"scorecard:{name}: central score <=2 requires repair")
        proof(row, f"scorecard:{name}")
    check.require(dimensions.issubset(scores), "scorecard: missing required dimensions")
    check.require(any(row.get("central") is True for row in scores.values()), "scorecard: identify central dimensions")
    for dimension in ("implementation", "integration", "visual", "motion", "3d"):
        gates = receipt.get("craft_gates", {})
        gate = gates.get(dimension) if isinstance(gates, dict) else None
        if not check.require(isinstance(gate, dict), f"gate:{dimension}: object required"):
            continue
        applicable = dimension not in ("motion", "3d") or profile.get(dimension)
        check.require(gate.get("status") == ("passed" if applicable else "not_applicable"), f"gate:{dimension}: unresolved or wrong applicability")
        check.fields(gate, ["observation"], f"gate:{dimension}")
        if applicable:
            proof(gate, f"gate:{dimension}", {"check"} if dimension == "implementation" else {"visual", "interaction"} if dimension in ("integration", "motion", "3d") else {"visual"})
    for key, flag, fields in (("motion_evidence", "motion", "trigger from to duration_easing interruption reduced_motion"), ("3d_evidence", "3d", "asset_source model_format texture_sizes renderer_dpr lighting camera performance_observation mobile_fallback")):
        for row in check.rows(receipt.get(key, []), key, required=bool(profile.get(flag))):
            check.fields(row, fields.split(), key)
            proof(row, key, {"interaction"} if flag == "motion" else {"visual", "interaction"})
    if profile.get("heavy_effects") or profile.get("3d"):
        budget = receipt.get("performance_budget")
        if check.require(isinstance(budget, dict), "performance_budget: object required"):
            check.fields(budget, "js_cost asset_weight texture_memory video draw_calls animation_work layout_work measured_result fallback".split(), "performance_budget")
            proof(budget, "performance_budget", {"check"})
    return check.result()


def platform_check(receipt, project):
    check = RecordCheck(project)
    if not check.require(isinstance(receipt, dict), "platform: receipt object required"):
        return check.result()
    path = check.file(receipt.get("platform_scout"), "platform_scout")
    if not path:
        return check.result()
    record = read_json(path)
    if not check.require(isinstance(record, dict), "platform: object required"):
        return check.result()
    check.require(record.get("schema") == "lobster-platform/v1", "platform: unsupported schema")
    check.strings(record.get("target_browsers"), "platform.target_browsers")
    try:
        checked = record.get("checked_at")
        check.require(isinstance(checked, str) and date.fromisoformat(checked).isoformat() == checked, "platform: ISO checked_at required")
    except ValueError:
        check.require(False, "platform: ISO checked_at required")
    evidence = {row["id"]: row for row in receipt.get("evidence", []) if isinstance(row, dict) and nonempty(row.get("id"))} if isinstance(receipt.get("evidence"), list) else {}
    seen = set()
    for row in check.rows(record.get("decisions"), "platform.decisions"):
        check.fields(row, "capability native_option library_option reason support_observation feature_detection fallback accessibility cost_comparison".split(), "platform decision")
        name = row.get("capability")
        if nonempty(name):
            check.require(name not in seen, "platform: duplicate capability")
            seen.add(name)
        check.require(row.get("choice") in ("native", "hybrid", "library"), "platform: explicit native/hybrid/library choice required")
        for url in check.strings(row.get("support_urls"), "platform.support_urls"):
            check.require(web_url(url), "platform: invalid support URL")
        check.file(row.get("support_evidence"), "platform.support_evidence")
        owner = check.file(row.get("implementation"), "platform.implementation")
        for field in ("evidence_ids", "fallback_evidence_ids"):
            for identity in check.strings(row.get(field), f"platform.{field}"):
                item = evidence.get(identity, {})
                check.require(item.get("status") == "passed" and item.get("kind") in (("interaction",) if field == "fallback_evidence_ids" else ("visual", "interaction")), f"platform.{field}: current observation required")
                check.file(item.get("artifact"), f"platform.{field}.artifact")
                owners = {path for subject in check.rows(item.get("subject_files"), f"platform.{field}.subjects") if (path := check.file(subject, f"platform.{field}.subject"))}
                check.require(owner is not None and owner in owners, f"platform.{field}: owner proof required")
    return check.result()


def verify(receipt, project: Path, require_platform=False) -> dict:
    if not isinstance(receipt, dict) or receipt.get("format") != "lobster-receipt/v2":
        result = verify_implementation(receipt, project)
        result["contract"] = "legacy-v1; does not satisfy v2 substantial-work gates"
        if require_platform:
            result["issues"].append("platform: receipt v2 required")
            result["status"] = "INCOMPLETE"
        return result
    legacy = dict(receipt, format="lobster-receipt/v1")
    result = verify_implementation(legacy, project)
    check = RecordCheck(project)
    check.issues.extend(result["issues"])
    check.issues.extend(craft_check(receipt, project)["issues"])
    if require_platform or "platform_scout" in receipt:
        check.issues.extend(platform_check(receipt, project)["issues"])
    summary = receipt.get("research")
    profile = receipt.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}
    required = isinstance(profile, dict) and any(profile.get(key) for key in ("substantial", "expressive", "motion", "3d"))
    if check.require(isinstance(summary, dict), "research summary required"):
        check.require(type(summary.get("required")) is bool, "research.required: boolean required")
        check.require(not required or summary.get("required") is True, "research cannot be waived for this profile")
        if summary.get("required") is True:
            path = check.file(summary.get("artifact"), "research.artifact")
            if path:
                research_record = read_json(path)
                check.issues.extend(research_verify(research_record, project, expressive=bool(profile.get("expressive")))["issues"])
                if isinstance(research_record, dict):
                    for key, target, field in (("sources_consulted", "sources", "name"), ("selected_references", "candidates", "name"), ("impact", "implementation_impacts", "change")):
                        actual = check.strings(summary.get(key), f"research.{key}")
                        expected = [row.get(field) for row in research_record.get(target, []) if isinstance(row, dict) and (target != "candidates" or row.get("status") in ("selected", "reference"))] if isinstance(research_record.get(target), list) else []
                        check.require(sorted(actual) == sorted(item for item in expected if isinstance(item, str)), f"research.{key}: differs from artifact")
                    evidence = {row["id"]: row for row in receipt.get("evidence", []) if isinstance(row, dict) and nonempty(row.get("id"))} if isinstance(receipt.get("evidence"), list) else {}
                    for row in check.rows(research_record.get("implementation_impacts"), "implementation_impacts"):
                        for identity in check.strings(row.get("evidence_ids"), "impact.evidence_ids"):
                            item = evidence.get(identity, {})
                            subjects = item.get("subject_files", [])
                            check.require(item.get("status") == "passed" and item.get("kind") in ("visual", "interaction") and isinstance(subjects, list) and row.get("implementation") in subjects, "research impact needs current visual/interaction owner proof")
                    candidates = research_record.get("candidates", [])
                    components = receipt.get("components", [])
                    if isinstance(candidates, list) and isinstance(components, list):
                        for candidate in candidates:
                            if isinstance(candidate, dict) and candidate.get("status") == "selected":
                                check.require(any(isinstance(component, dict) and component.get("origin") == "external" and component.get("source_url") == candidate.get("url") for component in components), "selected acquisition must match an integrated external component source_url")
        else:
            check.fields(summary, ["reason"], "research exemption")
    return check.result()


V3_STAGES = ("RECORD_VALID", "SOURCE_VERIFIED", "IMPLEMENTATION_VERIFIED", "EXECUTION_VERIFIED", "CRAFT_REVIEWED", "DELIVERY_READY")


def auto_profile(project: Path, brief: str = "") -> dict:
    root = Path(project).resolve(strict=True)
    source_suffixes = {".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".vue", ".svelte", ".html", ".py"}
    files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in source_suffixes and ".git" not in path.parts and "node_modules" not in path.parts]
    names = " ".join(path.name.lower() for path in files)
    text = (brief + " " + names).lower()
    categories = {
        "substantial": len(files) >= 8 or any(word in text for word in ("landing", "dashboard", "redesign", "app", "page")),
        "expressive": any(word in text for word in ("premium", "cinematic", "shader", "hero", "portfolio", "showcase")),
        "motion": any(word in text for word in ("motion", "animation", "transition", "scroll", "parallax", "gsap", "framer")),
        "3d": any(word in text for word in ("webgl", "three", "r3f", "gltf", "3d")),
        "forms": any(word in text for word in ("form", "input", "login", "settings")),
        "dense_data": any(word in text for word in ("table", "dashboard", "analytics", "grid", "data")),
        "interactive": any(word in text for word in ("button", "menu", "dialog", "modal", "command", "interactive")),
        "responsive": any(word in text for word in ("mobile", "responsive", "viewport", "breakpoint")),
    }
    if categories["substantial"]:
        categories["responsive"] = True
    required = ["research", "platform_scout", "browser_execution", "scenario_matrix", "craft_review"] if categories["substantial"] else ["technical_check"]
    if categories["dense_data"]: required.append("data_interface_craft")
    if categories["forms"]: required.append("form_craft")
    if categories["interactive"]: required.append("interaction_craft")
    return {"schema": "lobster-surface-profile/v1", "source": "auto", "project": str(root), "signals": categories, "required_gates": sorted(set(required)), "not_applicable": [name for name, enabled in (("3d", categories["3d"]), ("motion", categories["motion"])) if not enabled]}


def v3_verify(receipt, project: Path) -> dict:
    check = RecordCheck(project)
    if not check.require(isinstance(receipt, dict) and receipt.get("format") == "lobster-receipt/v3", "receipt: lobster-receipt/v3 required"):
        return check.result()
    for field in ("surface", "revision"):
        check.fields(receipt, [field], "receipt")
    stages = receipt.get("stages")
    if check.require(isinstance(stages, dict), "stages: object required"):
        for stage in V3_STAGES:
            value = stages.get(stage)
            check.require(value in ("PASS", "FAIL", "N/A"), f"stages.{stage}: PASS, FAIL or N/A required")
        for stage in V3_STAGES[1:]:
            if stages.get(stage) == "PASS":
                previous = V3_STAGES[V3_STAGES.index(stage) - 1]
                check.require(stages.get(previous) in ("PASS", "N/A"), f"stages.{stage}: previous stage {previous} is not closed")
    for field in ("profile", "research", "platform_scout", "provenance_lock", "dependency_graph", "scenario_run", "craft_review", "repair_ledger", "verdict"):
        check.file(receipt.get(field), f"receipt.{field}")
    verdict = receipt.get("verdict")
    if isinstance(verdict, dict) and "path" in verdict:
        verdict_path = check.file(verdict, "receipt.verdict")
        verdict = read_json(verdict_path) if verdict_path else {}
    if verdict and isinstance(verdict, dict):
        check.require(verdict.get("status") in ("DELIVERY_READY", "INCOMPLETE"), "verdict.status: invalid")
        if verdict.get("status") == "DELIVERY_READY":
            check.require(all(receipt.get("stages", {}).get(stage) in ("PASS", "N/A") for stage in V3_STAGES), "DELIVERY_READY requires every applicable stage closed")
    return check.result()


def plan(project: Path, brief: str = "") -> dict:
    profile = auto_profile(project, brief)
    return {"surface": Path(project).name, "class": "substantial frontend" if profile["signals"]["substantial"] else "scoped frontend edit", "required": profile["required_gates"], "optional": ["motion_craft"] if not profile["signals"]["motion"] else [], "not_applicable": profile["not_applicable"], "profile": profile}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lookup = commands.add_parser("discover")
    lookup.add_argument("--concept")
    lookup.add_argument("--capability")
    lookup.add_argument("--framework", default="")
    lookup.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("verify")
    check.add_argument("receipt", type=Path)
    check.add_argument("--project", type=Path, required=True)
    check.add_argument("--require-platform", action="store_true")
    draft = commands.add_parser("research", help="Create an unverified research record; host performs searches")
    draft.add_argument("--need", required=True)
    draft.add_argument("--framework", default="")
    draft.add_argument("--categories", default="components,motion")
    draft.add_argument("--out", type=Path, required=True)
    for name in ("research-verify", "craft-check"):
        command = commands.add_parser(name)
        command.add_argument("receipt", type=Path)
        command.add_argument("--project", type=Path, required=True)
        if name == "research-verify":
            command.add_argument("--expressive", action="store_true")
    for name in ("profile", "plan"):
        command = commands.add_parser(name)
        command.add_argument("--project", type=Path, required=True)
        command.add_argument("--brief", default="")
    v3 = commands.add_parser("verify-v3")
    v3.add_argument("receipt", type=Path)
    v3.add_argument("--project", type=Path, required=True)
    scout = commands.add_parser("scout")
    scout.add_argument("--project", type=Path, required=True)
    scout.add_argument("--brief", default="")
    for name in ("run", "inspect", "review", "provenance-check", "dependency-check", "repair-status", "status"):
        command = commands.add_parser(name)
        command.add_argument("--project", type=Path, required=True)
        command.add_argument("--input", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "research":
            result = research(args.need, args.framework, args.categories)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8") as output:
                output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps({"status": "DRAFT", "output": str(args.out.resolve()), "research_performed": False}))
            return 0
        if args.command == "profile":
            print(json.dumps(auto_profile(args.project, args.brief), ensure_ascii=False, indent=2))
            return 0
        if args.command == "plan":
            print(json.dumps(plan(args.project, args.brief), ensure_ascii=False, indent=2))
            return 0
        if args.command == "scout":
            profile = auto_profile(args.project, args.brief)
            print(json.dumps({"status": "READY", "profile": profile, "next": "Record exact platform support and fallback in platform-scout.json"}, ensure_ascii=False, indent=2))
            return 0
        if args.command in ("run", "inspect", "review"):
            result = {"status": "UNAVAILABLE", "command": args.command, "reason": "Use the browser adapter and independent review input; no execution or reviewer evidence was supplied"}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        if args.command in ("provenance-check", "dependency-check", "repair-status", "status"):
            result = {"status": "INCOMPLETE", "command": args.command, "reason": "v3 receipt index or input artifact is required"}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        if args.command == "discover":
            if not (args.concept and args.concept.strip() or args.capability and args.capability.strip()):
                parser.error("discover requires a nonempty --concept or --capability")
            result = discover(args.concept, args.capability, args.framework)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            summary = {name: {"status": value["status"],
                             "ids": [x["id"] for x in value.get("data", {}).get("matches", value.get("data", {}).get("candidates", []))],
                             **({"reason": value["reason"]} if "reason" in value else {})}
                       for name, value in result["results"].items()}
            print(json.dumps({"output": str(args.out.resolve()), "results": summary,
                              "next": "Read returned records; verify official source before acquisition."}, ensure_ascii=False))
            statuses = [r["status"] for r in result["results"].values()]
            return 2 if "ERROR" in statuses else 1 if "NO_MATCH" in statuses else 0
        record = read_json(args.receipt)
        if args.command == "verify-v3":
            result = v3_verify(record, args.project)
        elif args.command == "research-verify":
            result = research_verify(record, args.project, args.expressive)
        elif args.command == "craft-check":
            result = craft_check(record, args.project)
        else:
            result = verify(record, args.project, args.require_platform)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "READY_FOR_REVIEW" else 1
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
