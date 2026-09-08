#!/usr/bin/env node
// plief-lobster CLI shim — forwards to scripts/lobster.py using the best
// available Python. No dependencies, stdlib only on the Python side.
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const script = path.join(__dirname, "..", "scripts", "lobster.py");
const candidates = process.platform === "win32"
  ? ["py", "python", "python3"]
  : ["python3", "python"];

let last = null;
for (const exe of candidates) {
  const args = exe === "py" ? ["-3", script, ...process.argv.slice(2)] : [script, ...process.argv.slice(2)];
  const res = spawnSync(exe, args, { stdio: "inherit" });
  if (res.error && res.error.code === "ENOENT") { last = res.error; continue; }
  process.exit(res.status ?? 1);
}
console.error(`plief-lobster: no Python launcher found (${candidates.join(", ")}). Python 3.10+ is required.`);
if (last) console.error(String(last.message || last));
process.exit(2);
