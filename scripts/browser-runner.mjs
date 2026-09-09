#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync, statSync, lstatSync, readdirSync, mkdirSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { contain } from "./lib/contain.mjs";
import { projectFingerprint, DEFAULT_EXCLUDED_PATHS } from "./lib/fingerprint.mjs";

const args = process.argv.slice(2);
const value = name => args[args.indexOf(name) + 1];
const output = value("--out") || args[0];
const target = value("--base-url") || args[1];
const matrixPath = value("--matrix");
const projectRoot = resolve(value("--project") || process.cwd());
const dependencyGraph = value("--dependency-graph");
// Paths the run must leave out of the project fingerprint because they are written
// after it: the receipt index above all. Repeatable: --exclude <project-relative>.
const extraExcludes = args.reduce((acc, arg, index) => arg === "--exclude" && args[index + 1] ? [...acc, args[index + 1]] : acc, []);
if (!output || !target || !matrixPath) { console.error(JSON.stringify({status: "ERROR", reason: "usage: browser-runner.mjs --project <dir> --base-url <url> --matrix <scenario.json> --out <run.json>"})); process.exit(2); }
const sha256 = bytes => createHash("sha256").update(bytes).digest("hex");
// The fingerprint lives in scripts/lib/fingerprint.mjs so that scripts/lobster.py can
// recompute it from the spec the run declares. I9: an uncomputable fingerprint is an
// error, never a placeholder string.
function treeFingerprint(root) {
  try { return projectFingerprint(root, extraExcludes.length ? {excluded_paths: [...DEFAULT_EXCLUDED_PATHS, ...extraExcludes]} : {}); }
  catch (error) { return fail("fingerprint-project", root, String(error?.message || error)); }
}
const fail = (operation, path, reason) => { console.error(JSON.stringify({status: "ERROR", operation, path, root: projectRoot, reason})); process.exit(2); };
// I4/I7: a scenario-supplied path is resolved against the project root, never the
// process cwd. The decision lives in scripts/lib/contain.mjs so the Node adapters and
// scripts/lobster.py cannot drift apart.
const insideProject = raw => contain(projectRoot, raw).path;
const matrix = JSON.parse(readFileSync(matrixPath, "utf8"));
const scenarioHash = sha256(readFileSync(matrixPath));
const screenshotTargets = new Map();
for (const scenario of matrix.scenarios || []) {
  for (const step of scenario.steps || []) {
    if (step.action !== "screenshot") continue;
    const resolved = insideProject(step.path);
    if (!resolved) fail("validate-scenario-matrix", String(step.path), `scenario ${scenario.id}: screenshot path must be project-relative and stay inside the project root`);
    screenshotTargets.set(step, resolved);
  }
}
let playwright;
try { playwright = await import("playwright"); } catch {
  const result = {schema: "lobster-runtime/v2", status: "UNAVAILABLE", target, reason: "Playwright is not installed; host must provide an equivalent browser adapter", runtime_errors: [], network_errors: [], scenarios: []};
  writeFileSync(output, JSON.stringify(result, null, 2) + "\n"); console.log(JSON.stringify(result)); process.exit(1);
}
const fingerprintResult = treeFingerprint(projectRoot);
let revision = "working-tree"; try { revision = execFileSync("git", ["-C", projectRoot, "rev-parse", "HEAD"], {encoding: "utf8"}).trim(); } catch {}
let dependencyFingerprint = "unknown";
if (dependencyGraph && existsSync(dependencyGraph)) { try { dependencyFingerprint = JSON.parse(readFileSync(dependencyGraph, "utf8")).fingerprint || sha256(readFileSync(dependencyGraph)); } catch { dependencyFingerprint = sha256(readFileSync(dependencyGraph)); } }
const browser = await playwright.chromium.launch({headless: true});
const page = await browser.newPage();
let active = null;
page.on("console", message => { if (active && message.type() === "error") active.consoleErrors.push(message.text()); });
page.on("pageerror", error => { if (active) active.pageErrors.push(String(error)); });
page.on("requestfailed", request => { if (active) active.networkErrors.push({url: request.url(), error: request.failure()?.errorText || "request failed"}); });
page.on("response", response => { if (active && response.status() >= 400) active.networkErrors.push({url: response.url(), status: response.status()}); });
const locatorFor = locator => locator?.role ? page.getByRole(locator.role, {name: locator.name}) : locator?.label ? page.getByLabel(locator.label) : locator?.placeholder ? page.getByPlaceholder(locator.placeholder) : locator?.testId ? page.getByTestId(locator.testId) : locator?.text ? page.getByText(locator.text) : locator?.css ? page.locator(locator.css) : null;
const waitReadiness = async readiness => {
  if (!readiness) return;
  if (readiness.url && page.url() !== new URL(readiness.url, target).toString()) throw new Error(`readiness URL failed: ${page.url()}`);
  if (readiness.visible) await locatorFor(readiness.visible).waitFor({state: "visible"});
  if (readiness.domMarker) await page.locator(`[data-lobster-ready="${readiness.domMarker}"]`).waitFor({state: "visible"});
  if (readiness.responseUrl) await page.waitForResponse(response => response.url().includes(readiness.responseUrl) && response.ok(), {timeout: readiness.timeoutMs || 5000});
};
const actualFor = async (handle, assertion) => {
  if (assertion.assert === "visible") return await handle.isVisible();
  if (assertion.assert === "hidden") return await handle.isHidden();
  if (assertion.assert === "enabled") return await handle.isEnabled();
  if (assertion.assert === "disabled") return !(await handle.isEnabled());
  if (assertion.assert === "focused") return await handle.evaluate(element => element === document.activeElement);
  if (assertion.assert === "text") return await handle.innerText();
  if (assertion.assert === "url") return page.url();
  if (assertion.assert === "noConsoleErrors") return active.consoleErrors.length === 0;
  if (assertion.assert === "noPageErrors") return active.pageErrors.length === 0;
  if (assertion.assert === "noFailedRequests") return active.networkErrors.length === 0;
  if (assertion.assert === "noHorizontalOverflow") return await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  throw new Error(`unsupported assertion: ${assertion.assert}`);
};
const scenarios = [];
for (const scenario of matrix.scenarios || []) {
  const started = new Date().toISOString(); const failures = []; const assertionResults = []; const artifacts = [];
  active = {consoleErrors: [], pageErrors: [], networkErrors: []};
  try {
    if (scenario.capability_overrides?.reduced_motion) await page.emulateMedia({reducedMotion: scenario.capability_overrides.reduced_motion === "reduce" ? "reduce" : "no-preference"});
    if (scenario.viewport) await page.setViewportSize({width: scenario.viewport.width, height: scenario.viewport.height});
    await page.goto(target, {waitUntil: "domcontentloaded"}); await waitReadiness(scenario.readiness);
    for (const step of scenario.steps || []) {
      const handle = locatorFor(step.locator);
      if (step.action === "goto") await page.goto(new URL(step.url, target).toString(), {waitUntil: "domcontentloaded"});
      else if (step.action === "click") await handle.click(); else if (step.action === "doubleClick") await handle.dblclick();
      else if (step.action === "fill") await handle.fill(step.value ?? ""); else if (step.action === "clear") await handle.fill("");
      else if (step.action === "press") await (handle || page).press(step.key); else if (step.action === "hover") await handle.hover();
      else if (step.action === "focus") await handle.focus(); else if (step.action === "tab") await page.keyboard.press("Tab");
      else if (step.action === "scroll") await page.mouse.wheel(step.x || 0, step.y || 500);
      else if (step.action === "resize") await page.setViewportSize({width: step.width, height: step.height});
      else if (step.action === "reload") await page.reload({waitUntil: "domcontentloaded"}); else if (step.action === "back") await page.goBack({waitUntil: "domcontentloaded"});
      else if (step.action === "forward") await page.goForward({waitUntil: "domcontentloaded"}); else if (step.action === "select") await handle.selectOption(step.value);
      else if (step.action === "drag") await handle.dragTo(locatorFor(step.target)); else if (step.action === "waitFor") await page.waitForTimeout(step.ms || 100);
      else if (step.action === "screenshot") { const target = screenshotTargets.get(step); mkdirSync(dirname(target), {recursive: true}); await page.screenshot({path: target}); if (existsSync(target)) artifacts.push({kind: "screenshot", path: relative(projectRoot, target).replaceAll("\\", "/"), sha256: sha256(readFileSync(target))}); }
      else failures.push(`unsupported action: ${step.action}`);
    }
    for (const assertion of scenario.assertions || []) { const handle = locatorFor(assertion.locator); try { const actual = await actualFor(handle, assertion); const expected = (assertion.assert === "text" || assertion.assert === "url") ? assertion.value : true; const pass = assertion.assert === "text" ? (assertion.contains ? actual.includes(assertion.value) : actual === assertion.value) : actual === expected; assertionResults.push({assert: assertion.assert, status: pass ? "PASS" : "FAIL", expected, actual}); if (!pass) failures.push(`${assertion.assert} assertion failed`); } catch (error) { assertionResults.push({assert: assertion.assert, status: "FAIL", expected: assertion.value ?? true, actual: String(error)}); failures.push(String(error)); } }
  } catch (error) { failures.push(String(error)); }
  scenarios.push({id: scenario.id, status: failures.length || active.consoleErrors.length || active.pageErrors.length || active.networkErrors.length ? "FAIL" : "PASS", viewport: page.viewportSize(), steps: scenario.steps || [], assertions: assertionResults, failures, console_errors: [...active.consoleErrors], page_errors: [...active.pageErrors], runtime_errors: [...active.pageErrors, ...active.consoleErrors], network_errors: [...active.networkErrors], artifacts, started_at: started, finished_at: new Date().toISOString()});
}
const runtimeErrors = scenarios.flatMap(item => item.runtime_errors); const networkErrors = scenarios.flatMap(item => item.network_errors);
const result = {schema: "lobster-runtime/v3", status: runtimeErrors.length || networkErrors.length || scenarios.some(item => item.status === "FAIL") ? "FAIL" : "PASS", target, runner: "lobster-browser", runner_version: "3.1.3", browser_engine: "chromium", browser_version: browser.version(), run_id: `RUN-${Date.now()}`, started_at: new Date().toISOString(), finished_at: new Date().toISOString(), project_revision: revision, scenario_hash: scenarioHash, project_fingerprint: fingerprintResult.fingerprint, fingerprint_spec: fingerprintResult.spec, dependency_fingerprint: dependencyFingerprint, runtime_errors: runtimeErrors, network_errors: networkErrors, scenarios};
writeFileSync(output, JSON.stringify(result, null, 2) + "\n"); await browser.close(); console.log(JSON.stringify(result)); process.exit(result.status === "PASS" ? 0 : 1);
