# MapSource

## Current state
- Path resolution rests on one authority. `project_root()` resolves the target root **exactly once per invocation** and raises `ProjectPathError` naming the operation and the path; `contain()` is the single containment decision for every record-supplied path and reports why it refused (`empty` / `not-relative` / `escapes`). `RecordCheck.file`, `verify_implementation.file_ref` and the v3 cross-artifact joins all delegate to it — there is no second implementation left in the package.
- Entry points (`verify`, `v3_verify`) resolve the root and thread it down through `verify_implementation`, `craft_check`, `platform_check`, `research_verify` and `validate_artifact` as an explicit `root=` argument. Only an entry point may call `project_root()`.
- The Node adapters share `scripts/lib/contain.mjs`, which mirrors the Python rule and is exercised against `node:path.posix` and `node:path.win32`. `doctor` reports `path_containment: SHARED`.
- `v3_verify` validates the runner's own `scenario_run.scenarios[].artifacts[].path`: containment, hash freshness, and agreement with the evidence manifest.
- `STAGE_CONTRACT` is published in every `verify-v3` result. `RECORD_VALID` means the whole record is structurally valid and gates the stages below it; cross-artifact findings are attributed to the stage whose claim they break.
- The golden delivery is root-portable and verifies identically from any root and any cwd.
- **`project_fingerprint` is now verified.** `lobster-fingerprint/v1` (`scripts/lib/fingerprint.mjs` + `scripts/lobster.py`) is deterministic by construction: entries sorted by UTF-8 bytes, digest built from length-delimited fields with no serializer involved, separators normalised, symlinks recorded as leaves and never followed, and the exclusion spec folded into the digest header so a digest cannot be replayed under a wider scope. The run declares its scope; the verifier rebuilds the digest from disk. The scope may only omit `artifacts/` (covered by the evidence manifest), `proof/`, `.plif/`, `.lobster/` (covered by the receipt index) and the receipt itself — whose exclusion is **proved by content**, not accepted from a caller. Run records are `lobster-runtime/v3`; a v2 run reports `LOBSTER_PROJECT_FINGERPRINT_UNVERIFIABLE`.

## Verified
- Full unittest suite: **131 passed, 1 skipped** (`test_fingerprint.py` adds 23).
- Fingerprint tampering detection, end to end on the golden: modifying `server.py` (a covered file that is **not** a dependency-graph node, so no other chain sees it) → `LOBSTER_PROJECT_FINGERPRINT_STALE` and `EXECUTION_VERIFIED: FAIL`; adding an untracked file → STALE + `FILE_COUNT`; deleting a covered file → STALE; widening the scope to hide the change → `LOBSTER_FINGERPRINT_SCOPE_TOO_NARROW`; forging `file_count` → STALE; downgrading to runtime/v2 → `UNVERIFIABLE`. Editing `proof/` does **not** move the fingerprint and is caught by the receipt chain instead, which is exactly why it is excluded.
- Cross-implementation equality: `scripts/lib/fingerprint.mjs` and `scripts/lobster.py` produce byte-identical digests on a tree with Unicode names, spaces, deep nesting and mixed-case siblings.
- Golden migrated to `lobster-runtime/v3` by **real re-execution** (Chromium 153.0.8010.12, foreign cwd, 3/3 PASS), then re-chained; `verify-v3` → DELIVERY_READY, 0 issues, exit 0.
- Earlier rounds' proofs are unchanged: containment (16 tests), closure contracts (19), authority audit static+dynamic (7), v2 adversarial (15 attacks), path adversarial (11 attacks).

## Suspicion zone
- **medium — cross-platform is UNPROVEN, not failed.** No Linux kernel was available here (no WSL, no container, `PosixPath` not instantiable on Windows). `.github/workflows/ci.yml` runs the suite on `ubuntu-latest` and `windows-latest`; `DELIVERY_READY_CROSS_PLATFORM` may be claimed only when both legs are green for the same commit. See `tests/CROSS-PLATFORM.md` for the exact list of unexecuted POSIX behaviour (ext4 symlinks, permission bits, case sensitivity, POSIX-legal filenames).
- low: the golden's `proof/scenario-run.json` records `runner_version: 3.1.2`, the runner that actually produced it. The shipped runner is 3.1.3; the record is an honest attestation of the run, not a stale value to overwrite.
- low: `RECORD_VALID` deliberately double-counts the structural findings of the stages below it — published gate semantics, not duplicate reporting.
- low: Sifr and Orun remain `UNAVAILABLE` standalone; one test is skipped for their absence. Optional by contract; the core is `READY` without them.
