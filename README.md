# Pli'ef Lobster v3

Frontend orchestration with retained research and independent craft review.

Version 3 adds a closed verification loop: automatic surface profile, scenario planning, browser/runtime adapters, dependency fingerprints, owner-bound evidence and staged delivery truth. It refuses to upgrade a written claim into execution proof.

Version 2.1 adds [Platform Capability Scout](references/platform-capability-scout.md) before dependency selection. Applicable new work attaches browser-support, native/hybrid/library decisions and exercised fallback evidence, then runs `verify --require-platform`. Plain verify still reads earlier receipts and validates any Scout attached.

Load SKILL.md through your skill host. Keep plief-sifr and plief-orun as sibling folders for local discovery; this ZIP does not bundle them. Missing companions are reported as ERROR by discover. Python 3.10+ is required for the standard-library CLI; web/browser/MCP capabilities belong to the host.

From this folder run `python scripts/lobster.py --help` for commands. Use [research-contract](references/research-contract.md) for draft, verification, schema and migration instructions. The draft is intentionally incomplete until real research is recorded. Local tests: `python -m unittest discover -s tests -v`. The sibling integration case skips explicitly when those separate packages are unavailable.

The entrypoint routes domain references. scripts/lobster.py retains local discovery, checks current file hashes, research decisions and independent craft evidence. evals/cases contains behavioral scenarios for an agent to execute; unit tests do not establish visual skill effectiveness.

V2 retains legacy v1 receipt reading, but substantial builds require v2 gates. The CLI does not browse, install components, render, certify licensing or judge beauty. Human/agent inspection of the actual experience remains necessary. No third-party runtime dependency was added.

License: Apache-2.0. See LICENSE and NOTICE.md.
