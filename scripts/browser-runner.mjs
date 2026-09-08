#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const output = process.argv[2];
const target = process.argv[3];
if (!output || !target) {
  console.error(JSON.stringify({status: "ERROR", reason: "usage: browser-runner.mjs <output.json> <url>"}));
  process.exit(2);
}
let playwright;
try { playwright = await import("playwright"); } catch (error) {
  const result = {schema: "lobster-runtime/v1", status: "UNAVAILABLE", target, reason: "Playwright is not installed; host must provide an equivalent browser adapter", runtime_errors: [], scenarios: []};
  writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify(result));
  process.exit(1);
}
const browser = await playwright.chromium.launch({headless: true});
const page = await browser.newPage();
const runtimeErrors = [];
page.on("console", message => { if (message.type() === "error") runtimeErrors.push(message.text()); });
page.on("pageerror", error => runtimeErrors.push(String(error)));
await page.goto(target, {waitUntil: "networkidle"});
const result = {schema: "lobster-runtime/v1", status: runtimeErrors.length ? "FAIL" : "PASS", target, runtime_errors: runtimeErrors, scenarios: [{id: "initial-load", status: runtimeErrors.length ? "FAIL" : "PASS", url: page.url()}]};
writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
await browser.close();
console.log(JSON.stringify(result));
process.exit(runtimeErrors.length ? 1 : 0);
