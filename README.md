# Pli'ef Lobster v3.1

Frontend orchestration with retained research and independent craft review.

Version 3.1 makes proof authoritative: stages and verdicts are computed from semantically validated child artifacts, cross-artifact hashes, runtime attestation, evidence ownership and independent craft review. Receipt stage claims and verdict pointers are ignored.

Version 3 adds a closed verification loop: automatic surface profile, scenario planning, browser/runtime adapters, dependency fingerprints, owner-bound evidence and staged delivery truth. A missing browser, stale hash, failed assertion or absent review remains incomplete.

Version 2.1 adds [Platform Capability Scout](references/platform-capability-scout.md) before dependency selection. Applicable new work attaches browser-support, native/hybrid/library decisions and exercised fallback evidence, then runs `verify --require-platform`. Plain verify still reads earlier receipts and validates any Scout attached.

Load SKILL.md through your skill host. Optional integrations are resolved by `PLIEF_SIFR_PATH`, `PLIEF_ORUN_PATH`, `~/.plief/lobster/config.json`, host registry, and finally a development-only sibling fallback. The standalone ZIP never guesses URLs and reports unavailable integrations honestly. Python 3.10+ is required for the standard-library CLI; web/browser/MCP capabilities belong to the host.

From this folder run `python scripts/lobster.py --help` for commands. Use [research-contract](references/research-contract.md) for draft, verification, schema and migration instructions. The draft is intentionally incomplete until real research is recorded. Local tests: `python -m unittest discover -s tests -v`. The sibling integration case skips explicitly when those separate packages are unavailable.

The entrypoint routes domain references. `scripts/lobster.py verify-v3` computes the proof state from the indexed artifacts; `scripts/browser-runner.mjs` executes the closed scenario matrix when Playwright is provided; `scripts/dependency-graph.mjs` emits a deterministic local import graph. `evals/cases` contains behavioral scenarios for an agent to execute; unit tests do not establish visual skill effectiveness.

v3 is current; v2 and v1 are LEGACY receipt reading, but substantial builds require v2 gates. The CLI does not browse, install components, render, certify licensing or judge beauty. Human/agent inspection of the actual experience remains necessary. No third-party runtime dependency was added.

License: Apache-2.0. See LICENSE and NOTICE.md.

