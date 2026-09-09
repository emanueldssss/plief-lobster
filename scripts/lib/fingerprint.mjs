// lobster-fingerprint/v1 — a deterministic, verifiable project fingerprint.
//
// The digest must be reproducible by scripts/lobster.py from the spec alone, so the
// algorithm avoids every ambiguous step:
//
//   * entries are sorted by the UTF-8 BYTES of the project-relative path, never by
//     localeCompare, whose result depends on the host's ICU locale;
//   * the digest is built incrementally from length-delimited fields, never from
//     JSON.stringify, whose escaping rules differ between JS and Python;
//   * separators are normalised to "/" so Windows and POSIX agree;
//   * symlinks are recorded as a leaf and never followed, so a link loop cannot
//     recurse and a link's target cannot silently join the covered set.
//
// The exclusion spec is folded into the digest header: a fingerprint therefore
// attests to WHAT it covered, and a digest cannot be replayed under a wider spec.
import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

export const FINGERPRINT_SCHEMA = "lobster-fingerprint/v1";
export const ALGORITHM = "sha256-file-list/v1";

// Directories excluded by NAME at any depth: never project source.
export const DEFAULT_EXCLUDED_DIRECTORIES = ["node_modules", ".git"];
// Project-relative path prefixes excluded because another verified hash chain already
// covers them: `artifacts/` by the evidence manifest, `proof/` by the receipt index.
// Excluding them is what makes the fingerprint stable while evidence is being written.
export const DEFAULT_EXCLUDED_PATHS = ["artifacts", "proof"];

export function fingerprintSpec(overrides = {}) {
  return {
    schema: FINGERPRINT_SCHEMA,
    algorithm: ALGORITHM,
    excluded_directories: [...(overrides.excluded_directories || DEFAULT_EXCLUDED_DIRECTORIES)].sort(),
    excluded_paths: [...(overrides.excluded_paths || DEFAULT_EXCLUDED_PATHS)].sort(),
    symlink_policy: "record-as-leaf",
  };
}

const sha256 = bytes => createHash("sha256").update(bytes).digest("hex");

/** Collect [relativePath, value] entries covered by `spec`. Throws on an unreadable tree. */
export function collectEntries(root, spec) {
  const excludedDirs = new Set(spec.excluded_directories);
  const excludedPaths = new Set(spec.excluded_paths);
  const entries = [];
  const walk = dir => {
    for (const name of readdirSync(dir)) {
      if (excludedDirs.has(name)) continue;
      const full = join(dir, name);
      const rel = relative(root, full).split(/[\\/]/).join("/");
      if (excludedPaths.has(rel)) continue;
      const stat = lstatSync(full);
      if (stat.isSymbolicLink()) entries.push([rel, "symlink"]);
      else if (stat.isDirectory()) walk(full);
      else entries.push([rel, sha256(readFileSync(full))]);
    }
  };
  walk(root);
  entries.sort((a, b) => Buffer.from(a[0], "utf8").compare(Buffer.from(b[0], "utf8")));
  return entries;
}

/** The digest itself. `entries` may be passed in to avoid walking twice. */
export function digestFor(spec, entries) {
  const hash = createHash("sha256");
  hash.update(Buffer.from(`${FINGERPRINT_SCHEMA}\n${ALGORITHM}\n`, "utf8"));
  hash.update(Buffer.from(`dirs:${spec.excluded_directories.join(",")}\n`, "utf8"));
  hash.update(Buffer.from(`paths:${spec.excluded_paths.join(",")}\n`, "utf8"));
  hash.update(Buffer.from(`symlinks:${spec.symlink_policy}\n`, "utf8"));
  for (const [rel, value] of entries) {
    hash.update(Buffer.from(rel, "utf8"));
    hash.update(Buffer.from([0]));
    hash.update(Buffer.from(value, "utf8"));
    hash.update(Buffer.from([10]));
  }
  return hash.digest("hex");
}

/** Returns {fingerprint, spec} for `root`. */
export function projectFingerprint(root, overrides = {}) {
  const spec = fingerprintSpec(overrides);
  const entries = collectEntries(root, spec);
  return {fingerprint: digestFor(spec, entries), spec: {...spec, file_count: entries.length}};
}
