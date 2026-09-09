# Cross-platform status

## The rule

`DELIVERY_READY` and `DELIVERY_READY_CROSS_PLATFORM` are **different claims**.

```
DELIVERY_READY                  the suite passes on the host it was run on
DELIVERY_READY_CROSS_PLATFORM   the SAME suite, at the SAME commit, passes on
                                real POSIX and real Windows
```

`DELIVERY_READY_CROSS_PLATFORM` may be asserted **only** when the `verify` matrix in
`.github/workflows/ci.yml` is green on `ubuntu-latest` **and** `windows-latest` for the
commit in question. Nothing else counts: not a Windows-only run, not a POSIX simulation,
not a code reading. If you have not seen both legs green, write
`DELIVERY_READY_CROSS_PLATFORM = UNPROVEN` and say which leg is missing.

## What is proven today

POSIX is no longer a simulation. GitHub Actions ran the full suite on a real Linux
kernel at commit `d4fd42a`:

| Leg | Result at `d4fd42a` |
|---|---|
| `ubuntu-latest` / Python 3.12 | **PASS** |
| `ubuntu-latest` / Python 3.13 | **PASS** |
| `windows-latest` / Python 3.12 | FAIL — fixed, see below |
| `windows-latest` / Python 3.13 | FAIL — fixed, see below |

So every POSIX behaviour previously listed as unexecuted — ext4 symlink resolution
through `Path.resolve()`, permission bits, case-sensitive filesystems, POSIX-legal
filenames — has now actually run and passed. The `cross-platform-gate` job was skipped
because the Windows legs failed, so `DELIVERY_READY_CROSS_PLATFORM` was **not** claimed.

Also proven, on Windows locally and in CI:

| Concern | Proof |
|---|---|
| Containment classification | `test_closure.CrossPlatformContainmentTests` runs 15 refused and 10 accepted spellings through `contain()` under `PurePosixPath`/`PureWindowsPath` **and** `node:path.posix`/`node:path.win32`, asserting Node and Python agree spelling for spelling |
| Root-spelling invariance | `test_paths.RootSpellingInvarianceTests` — the same physical root spelled raw, resolved, via `project_root()`, with a trailing separator, with a `.` segment, and through a junction must yield the same containment decision |
| Fingerprint determinism | `test_fingerprint.AlgorithmTests` — locale-independent ordering, root-independence, cwd-independence, byte-for-byte equality with `scripts/lib/fingerprint.mjs` |

The containment rule is deliberately the **union** of POSIX and Windows restrictions, so
a record accepted on one host is accepted on the other.

## The Windows divergence found by CI at `d4fd42a`

`contain()` resolved the candidate path but compared it against the root **exactly as
given**. A root spelled non-canonically — a junction or reparse point, or an 8.3 short
name such as the `RUNNER~1` temporary directories GitHub Actions hands out on Windows —
therefore compared unequal to itself, and a legitimate project-relative path was refused
as an escape. The visible symptom was a valid receipt exclusion reported as
`LOBSTER_FINGERPRINT_SCOPE_TOO_NARROW:excluded_paths:receipt-final.json`.

It did not reproduce locally because the local temporary directory happened to be
canonical. This is the concrete reason a local run is not a substitute for CI.

`contain()` now compares against the canonical root when, and only when, the direct
comparison fails, so an already-canonical root — the runtime case, since `project_root()`
produces one — costs nothing. `project_root()` remains the only authority that
*establishes* a root; nothing else was given the power to define one.

## Known cross-platform hazards, and what guards them

1. **Line endings.** The fingerprint hashes file *bytes*. A checkout that converts CRLF
   would invalidate a valid receipt on the other platform. `.gitattributes` sets `* -text`
   so nothing is converted, and the CI workflow fails if the checkout is dirty.
2. **Windows junctions.** Node's `lstat` reports a junction as a symbolic link; `pathlib`
   reports it as a directory. Unaligned, the runner and the verifier walk different trees
   and disagree on the digest. `is_link()` in `scripts/lobster.py` reads the reparse tag so
   both sides agree; on POSIX the tag does not exist and the symlink check alone applies.
3. **Non-canonical roots.** A junction, reparse point or 8.3 short name is a different
   spelling of the same physical directory. Every containment comparison must have both
   sides canonical; see the divergence above.
4. **Locale-dependent sorting.** `Array.prototype.localeCompare` depends on the host's ICU
   data. The fingerprint sorts by UTF-8 bytes in both implementations instead.
5. **Serializer differences.** `JSON.stringify` and `json.dumps` escape differently. The
   digest is built from length-delimited fields and never passes through a serializer.

## Running the suite

```bash
cd tests && python -m unittest discover -v
```

Browser proofs need Playwright with Chromium; tests that require it skip cleanly when it
is absent, so a green run without Playwright is a **partial** run. The CI workflow always
installs it, so a green CI leg is a full run.
