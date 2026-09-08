#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const args = process.argv.slice(2);
const value = name => args[args.indexOf(name) + 1];
const output = value("--out") || args[0];
const target = value("--base-url") || args[1];
const matrixPath = value("--matrix");
if (!output || !target || !matrixPath) {
  console.error(JSON.stringify({status: "ERROR", reason: "usage: browser-runner.mjs --project <dir> --base-url <url> --matrix <scenario.json> --out <run.json>"}));
  process.exit(2);
}
let playwright;
try { playwright = await import("playwright"); } catch (error) {
  const result = {schema: "lobster-runtime/v2", status: "UNAVAILABLE", target, reason: "Playwright is not installed; host must provide an equivalent browser adapter", runtime_errors: [], scenarios: []};
  writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify(result));
  process.exit(1);
}
const browser = await playwright.chromium.launch({headless: true});
const page = await browser.newPage();
const runtimeErrors = [];
page.on("console", message => { if (message.type() === "error") runtimeErrors.push(message.text()); });
page.on("pageerror", error => runtimeErrors.push(String(error)));
const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
const scenarios = [];
for (const scenario of matrix.scenarios || []) {
  const started = new Date().toISOString();
  const failures = [];
  try {
    await page.goto(target, {waitUntil: "networkidle"});
    for (const step of scenario.steps || []) {
      const locator = step.locator || {};
      const handle = locator.role ? page.getByRole(locator.role, {name: locator.name}) : locator.label ? page.getByLabel(locator.label) : locator.placeholder ? page.getByPlaceholder(locator.placeholder) : locator.testId ? page.getByTestId(locator.testId) : locator.css ? page.locator(locator.css) : locator.text ? page.getByText(locator.text) : null;
      if (step.action === "goto") await page.goto(new URL(step.url, target).toString());
      else if (step.action === "click") await handle.click();
      else if (step.action === "fill") await handle.fill(step.value ?? "");
      else if (step.action === "clear") await handle.fill("");
      else if (step.action === "press") await (handle || page).press(step.key);
      else if (step.action === "hover") await handle.hover();
      else if (step.action === "focus") await handle.focus();
      else if (step.action === "tab") await page.keyboard.press("Tab");
      else if (step.action === "scroll") await page.mouse.wheel(step.x || 0, step.y || 500);
      else if (step.action === "resize") await page.setViewportSize({width: step.width, height: step.height});
      else if (step.action === "reload") await page.reload();
      else if (step.action === "waitFor") await page.waitForTimeout(step.ms || 100);
      else if (step.action === "screenshot") await page.screenshot({path: step.path});
      else failures.push(`unsupported action: ${step.action}`);
    }
    for (const assertion of scenario.assertions || []) {
      const handle = assertion.locator?.role ? page.getByRole(assertion.locator.role, {name: assertion.locator.name}) : assertion.locator?.label ? page.getByLabel(assertion.locator.label) : assertion.locator?.css ? page.locator(assertion.locator.css) : null;
      if (assertion.assert === "visible") await handle.isVisible();
      else if (assertion.assert === "hidden") await handle.isHidden();
      else if (assertion.assert === "focused") { if (!(await handle.evaluate(element => element === document.activeElement))) failures.push("focus assertion failed"); }
      else if (assertion.assert === "url" && page.url() !== assertion.value) failures.push("url assertion failed");
      else if (assertion.assert === "noConsoleErrors" && runtimeErrors.length) failures.push("console error assertion failed");
      else failures.push(`unsupported assertion: ${assertion.assert}`);
    }
  } catch (error) { failures.push(String(error)); }
  scenarios.push({id: scenario.id, status: failures.length || runtimeErrors.length ? "FAIL" : "PASS", viewport: page.viewportSize(), steps: scenario.steps || [], assertions: scenario.assertions || [], runtime_errors: [...runtimeErrors], network_errors: [], artifacts: [], started_at: started, finished_at: new Date().toISOString()});
}
const result = {schema: "lobster-runtime/v2", status: runtimeErrors.length || scenarios.some(item => item.status === "FAIL") ? "FAIL" : "PASS", target, runner: "lobster-browser", runner_version: "3.1.0", run_id: `RUN-${Date.now()}`, started_at: new Date().toISOString(), finished_at: new Date().toISOString(), scenario_hash: "provided-by-host", project_fingerprint: "provided-by-host", dependency_fingerprint: "provided-by-host", runtime_errors: runtimeErrors, scenarios};
writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
await browser.close();
console.log(JSON.stringify(result));
process.exit(runtimeErrors.length ? 1 : 0);
