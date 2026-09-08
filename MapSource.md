# MapSource

## Current state
- Lobster v3 proof authority hardening is implemented and committed at 91f3296.
- Golden dashboard receipt computes DELIVERY_READY with exit code 0.
- Evidence hashes are recalculated from physical files; dependency closure checks current node hashes.

## Verified
- Full unittest suite: 66 passed, 1 skipped.
- Adversarial mutations: screenshot tamper, missing evidence, fake review hash, stale dependency, fake before ID all return INCOMPLETE with exit 1.
- ZIP: outputs/plief-lobster-v3.1.zip SHA-256 3a9b0af3b4cbbef47c8aca66e74816ce1353759d5c3b19d50c5b58128af412d4.

## Suspicion zone
- medium: standalone browser execution depends on a host Playwright/Chromium installation; the packaged core verifier remains portable.
- low: L25-L48 live checks outside the golden browser scenarios were not available in this workspace.
- high: npm publish of `plief-lobster@3.1.0` was rejected by registry with HTTP 404/permission; npm credentials or package ownership is required.
