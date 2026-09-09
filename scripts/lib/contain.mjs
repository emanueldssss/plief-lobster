// The single containment decision for record-supplied paths in the Node adapters.
//
// It mirrors scripts/lobster.py `contain()` exactly, including invariant I10: the
// refusal rules are the UNION of POSIX and Windows rules on both hosts, so a record
// one host accepts is accepted by the other. `impl` is a node:path implementation
// (`path`, `path.posix` or `path.win32`) so the decision can be exercised for both
// platforms from either one.
import nodePath from "node:path";

/** True when `raw` is not a project-relative spelling, under either platform's rules. */
export function notRelative(raw) {
  if (typeof raw !== "string" || !raw.trim()) return true;
  const text = raw.trim();
  if (/^[a-zA-Z]:/.test(text)) return true;
  if (text.startsWith("/") || text.startsWith("\\")) return true;
  if (nodePath.posix.isAbsolute(text) || nodePath.win32.isAbsolute(text)) return true;
  return text.split(/[\\/]/).includes("..");
}

/**
 * Resolve `raw` against `root`. Returns {path, reason} where reason is null on
 * success and "empty" | "not-relative" | "escapes" otherwise.
 */
export function contain(root, raw, impl = nodePath) {
  if (typeof raw !== "string" || !raw.trim()) return {path: null, reason: "empty"};
  if (notRelative(raw)) return {path: null, reason: "not-relative"};
  const candidate = impl.resolve(root, raw.trim());
  const rel = impl.relative(root, candidate);
  const inside = rel !== "" && !rel.split(/[\\/]/).includes("..") && !impl.isAbsolute(rel);
  return inside ? {path: candidate, reason: null} : {path: null, reason: "escapes"};
}

/** True when an already-resolved absolute path lies strictly inside `root`. */
export function insideRoot(root, candidate, impl = nodePath) {
  const rel = impl.relative(root, candidate);
  return rel !== "" && !rel.split(/[\\/]/).includes("..") && !impl.isAbsolute(rel);
}
