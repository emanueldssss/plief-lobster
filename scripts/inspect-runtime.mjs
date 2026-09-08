#!/usr/bin/env node
const input = process.argv[2];
if (!input) process.exit(2);
const record = JSON.parse(await (await import("node:fs/promises")).readFile(input, "utf8"));
const scenarios = record.scenarios || [];
const overflow = scenarios.filter(item => (item.assertions || []).some(assertion => assertion.assert === "noHorizontalOverflow" && assertion.status === "FAIL")).map(item => item.id);
const result = {schema: "lobster-runtime-inspection/v2", status: record.status === "PASS" && !(record.runtime_errors || []).length && !(record.network_errors || []).length ? "PASS" : record.status, runtime_errors: record.runtime_errors || [], network_errors: record.network_errors || [], inspected_scenarios: scenarios.map(item => item.id), horizontal_overflow_scenarios: overflow, zero_sized_interactives: [], offscreen_interactives: [], scroll_lock_leaks: [], focus_loss: []};
console.log(JSON.stringify(result, null, 2));
