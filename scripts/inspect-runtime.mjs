#!/usr/bin/env node
const input = process.argv[2];
if (!input) process.exit(2);
const record = JSON.parse(await (await import("node:fs/promises")).readFile(input, "utf8"));
const result = {schema: "lobster-runtime-inspection/v1", status: record.status === "PASS" && !(record.runtime_errors || []).length ? "PASS" : record.status, runtime_errors: record.runtime_errors || [], network_errors: record.network_errors || [], inspected_scenarios: (record.scenarios || []).map(item => item.id)};
console.log(JSON.stringify(result, null, 2));
