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

Executed on Windows 11, Python 3.14.7, Node 24.19, Chromium 153.0.8010.12:

| Concern | Proof |
|---|---|
| Containment classification | `test_closure.CrossPlatformContainmentTests` runs 15 refused and 10 accepted spellings through `contain()` under `PurePosixPath`/`PureWindowsPath` **and** `node:path.posix`/`node:path.win32`, asserting Node and Python agree spelling for spelling |
| Containment arithmetic | `test_posix_root_semantics_are_exercised_with_pure_posix_paths` performs the root/relative arithmetic end to end with POSIX separators |
| Fingerprint determinism | `test_fingerprint.AlgorithmTests` — locale-independent ordering, root-independence, cwd-independence, and byte-for-byte equality with `scripts/lib/fingerprint.mjs` |

The containment rule is deliberately the **union** of POSIX and Windows restrictions, so
a record accepted on one host is accepted on the other.

## What is NOT proven today

No Linux kernel was available in the environment where this work was done: `wsl.exe`
reports WSL is not installed, there is no container runtime, and `pathlib.PosixPath`
cannot be instantiated on Windows (`UnsupportedOperation`). Therefore the following are
**unexecuted** and must be confirmed by the `ubuntu-latest` leg:

- ext4 symlink resolution through `Path.resolve()` and the containment test that follows it;
- POSIX permission bits (a directory or file that cannot be read, and the error text produced);
- case-sensitive filesystem behaviour, where `SRC/App.tsx` and `src/app.tsx` are distinct files;
- `os.lstat().st_reparse_tag` has no POSIX counterpart — `is_link()` falls back to
  `Path.is_symlink()`, which is the only path exercised there;
- real POSIX filename bytes, including names that are legal on Linux and illegal on
  Windows (`a\b`, `con`, a trailing space or dot).

## Known cross-platform hazards, and what guards them

1. **Line endings.** The fingerprint hashes file *bytes*. A checkout that converts CRLF
   would invalidate a valid receipt on the other platform. `.gitattributes` sets `* -text`
   so nothing is converted, and the CI workflow fails if the checkout is dirty.
2. **Windows junctions.** Node's `lstat` reports a junction as a symbolic link; `pathlib`
   reports it as a directory. Unaligned, the runner and the verifier walk different trees
   and disagree on the digest. `is_link()` in `scripts/lobster.py` reads the reparse tag so
   both sides agree; on POSIX the tag does not exist and the symlink check alone applies.
3. **Locale-dependent sorting.** `Array.prototype.localeCompare` depends on the host's ICU
   data. The fingerprint sorts by UTF-8 bytes in both implementations instead.
4. **Serializer differences.** `JSON.stringify` and `json.dumps` escape differently. The
   digest is built from length-delimited fields and never passes through a serializer.

## Running the suite

```bash
cd tests && python -m unittest discover -v
```

Browser proofs need Playwright with Chromium; tests that require it skip cleanly when it
is absent, so a green run without Playwright is a **partial** run. The CI workflow always
installs it, so a green CI leg is a full run.
