#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
const [project, output] = process.argv.slice(2);
if (!project || !output) process.exit(2);
const graph = {schema: "lobster-dependency-graph/v1", project, files: [], fingerprint: ""};
const hash = createHash("sha256");
const packageText = readFileSync(`${project}/package.json`, "utf8");
hash.update(packageText);
graph.files.push("package.json");
graph.fingerprint = hash.digest("hex");
writeFileSync(output, JSON.stringify(graph, null, 2) + "\n");
console.log(JSON.stringify(graph));
