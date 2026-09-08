#!/usr/bin/env node
import { readFileSync, existsSync, writeFileSync, statSync } from "node:fs";
import { resolve, relative, dirname } from "node:path";
import { createHash } from "node:crypto";

const [projectArg, entryArg, output] = process.argv.slice(2);
if (!projectArg || !entryArg || !output) process.exit(2);
const project = resolve(projectArg); const extensions = ["", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss"];
const nodes = new Map(); const edges = [];
function resolveImport(from, specifier) { if (!specifier.startsWith(".")) return null; for (const suffix of extensions) { const candidate = resolve(dirname(from), specifier + suffix); if (existsSync(candidate) && statSync(candidate).isFile()) return candidate; } return null; }
function visit(file) { const absolute = resolve(file); if (nodes.has(absolute) || !existsSync(absolute)) return; const bytes = readFileSync(absolute); const path = relative(project, absolute).replaceAll("\\", "/"); nodes.set(absolute, {path, sha256: createHash("sha256").update(bytes).digest("hex")}); const source = bytes.toString("utf8"); const imports = [...source.matchAll(/(?:import|export)\s+(?:[^'";]+?\s+from\s+)?["']([^"']+)["']/g)].map(match => match[1]); for (const specifier of imports) { const target = resolveImport(absolute, specifier); if (target) { const targetPath = relative(project, target).replaceAll("\\", "/"); edges.push({from: path, to: targetPath}); visit(target); } } }
visit(resolve(project, entryArg));
const sortedNodes = [...nodes.values()].sort((a,b) => a.path.localeCompare(b.path)); const sortedEdges = edges.sort((a,b) => `${a.from}->${a.to}`.localeCompare(`${b.from}->${b.to}`));
const fingerprint = createHash("sha256").update(JSON.stringify({nodes: sortedNodes, edges: sortedEdges})).digest("hex");
const graph = {schema: "lobster-dependency-graph/v2", entries: [relative(project, resolve(project, entryArg)).replaceAll("\\", "/")], nodes: sortedNodes, edges: sortedEdges, confidence: "FULL", fingerprint};
writeFileSync(output, JSON.stringify(graph, null, 2) + "\n"); console.log(JSON.stringify(graph));
