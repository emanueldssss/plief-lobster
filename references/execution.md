# Execution contract

## One state, explicit handoffs

Keep Sifr's ExperienceIR and DesignDNA authoritative. Lobster adds a discovery response and a delivery receipt; it does not create another design system or duplicate every IR field. Keep artifacts in the project's `.plif/artifacts/<surface-id>/`, outside publicly served directories. Reuse the same surface ID on follow-up edits and invalidate evidence for changed files.

| Stage | Input | Actual operation | Exit evidence |
| --- | --- | --- | --- |
| Frame | Brief, target, native code/render | Inspect task, content, stack, constraints | Product frame and preserve/extend/replace decision |
| Concept | Product need and reference | Execute Sifr query; read relevant laws and tensions | Dominant grammar in DNA and concept-to-code obligations |
| Source | Missing capability and native inventory | Execute Orun query; verify official source and real API | Candidate decision and usable acquisition route |
| Integrate | Selected part and slot contract | Acquire, adapt, mount, connect state | Actual implementation and use-site files |
| Inspect | Running surface and concept obligations | Exercise controls and inspect rendered states | Browser evidence tied to current source hashes |
| Deliver | Current implementation and evidence | Run checks; resolve material defects | Receipt integrity plus explicit reviewer verdict |

Move through stages within the same task. A handoff is a change of responsibility, not a reason to stop and ask the user to run another skill. Read sibling paths from the package root; do not assume a tool called `orun` exists.

## Concept materialization

For each chosen law, record:

`source concept ID or project reference → inherited principle → product consequence → implementation owner → visible/behavioral proof`

Example: a reference archive needs comparison across many records. An ordered typographic grid gives labels stable positions; row density and aligned dates support scanning; the narrow layout preserves each label/value pair. The implementation owner is the record list and its responsive rules. Evidence must show a long record, adjacent records, and the narrow transformation. Merely using a serif does not implement that principle.

Do not declare a concept applied because its ID appears in JSON. Judge topology, hierarchy, type roles, control language, and states against the selected laws. In a hybrid, identify which concept owns each dimension and reject incompatible rules. Do not average two conflicting grammars into generic cards.

Use a product-grounded thesis when the index has no suitable match. Label it authored; do not invent a catalog ID. Preserve an established project concept for a narrow repair instead of reselecting it.

## Native inventory and Orun acquisition

Read the packaged integration contracts in [`integrations/sifr.json`](../integrations/sifr.json) and [`integrations/orun.json`](../integrations/orun.json) at this handoff. Resolve the external implementation through Lobster's deterministic resolver.

1. Inspect existing components, exports, callers, tokens, installed packages, and configured registries. Record the actual files searched and why they do or do not satisfy the slot. `already_searched_native` describes work performed; it is not a ritual boolean.
2. Fill the host/provider query contract from observed project facts. Validate with the resolved integration only when its contract declares a validator.
3. Execute `lobster.py discover --capability ...` or the sibling query directly. Keep bounded candidates. Inspect a source profile only when its result is relevant. Zero matches or missing catalogs permit direct official research; they do not prove custom code is necessary.
4. Follow the official documentation to the exact package, registry item, or source file. Inspect source, license, dependencies, framework and styling assumptions, browser/server boundary, keyboard semantics, and lifecycle. Verify current facts using available web tools. Search ranking does not perform these checks.
5. Select and validate the local selection-record contract. Record inspected URLs/files, observed version or revision, and reasons for rejecting credible alternatives. Do not copy sample candidates or evidence URLs. Never fabricate `VERIFIED_CURRENT`.
6. Use the existing package manager and verified acquisition instructions. Inspect what will be added or overwritten. Carry out reversible project integration already authorized by the task; do not ask again merely because it adds a suitable dependency. Do not run unreviewed remote shell installers or authorize unrelated mutations.
7. Read the acquired code/API. Preserve the mechanism that earned selection. Map it to host tokens, routing, state, localization, focus, mobile behavior, and reduced motion. Remove demo copy and unnecessary runtime cost. Record source and material adaptations.
8. Mount it in the target's reachable render path and exercise its defining behavior. An installed dependency, unused import, detached demo, commented JSX, or file named after a library is not integration.

For a copied source, retain required notices and record source revision plus local destination. For a package, retain its resolved version/lockfile evidence and record wrapper/use-site. For native reuse, record the existing source. For custom work, record the failed fit or cost reason; do not claim vendor provenance.

When acquisition fails, classify once: unavailable source, access/license, incompatibility, dependency mismatch, or integration defect. Change the candidate or approach if a bounded retry cannot resolve it. Keep other authorized implementation moving; make any unmet named-provider requirement explicit.

## Delivery receipt

Use `lobster-receipt/v3` for new substantial work. `lobster-receipt/v3` and v1 are legacy compatibility contracts only. All file paths are project-relative. Each file object has `path` and `sha256` computed from actual bytes. Generate hashes after the final relevant edit. The verifier rejects absent or changed files, traversal, duplicate IDs, missing proof links, and external-component claims with no recorded source. It cannot tell whether evidence text is truthful; the reviewer must inspect it.

Required fields:

- `surface`, `route`: concrete target identifiers.
- `concepts[]`: `id`, `law`, `product_reason`, `implementation` (file object), and `evidence_ids` referencing visual or interaction evidence. Use at least three consequential laws for a new full visual direction; the generic verifier accepts one to support scoped component changes.
- `components[]`: `id`, `origin` (`native`, `external`, `custom`), `mechanism`, `implementation` (file object), `usage` (file object), `evidence_ids`. External entries also require `source_url`, `revision`, `license`, and `source_evidence` (file object containing the inspected source/license/version record). Custom entries require `reason`.
- `evidence[]`: `id`, `kind` (`visual`, `interaction`, `check`), `status` (`passed`, `failed`, `unverified`), `target`, `observation`, and `subject_files` (nonempty file objects for the code the evidence covers). Observed evidence requires an `artifact` file object. Unverified evidence requires a `reason` instead. Visual entries also require `viewport` as positive `[width, height]` and `state`.
- `limitations[]`: material gaps, including browser or source access limits. Empty only when none are known.

Record at least one visual observation, one exercised interaction, and one relevant technical check for a substantive interactive build. For a static surface, an interaction check can demonstrate its actual link/navigation behavior. Read-only audits and micro-edits do not require this receipt.

Store screenshots, test output, or trace/log evidence before referencing them. An interaction artifact can be a captured browser trace or a concise observation log recording the action and observed outcome; it cannot be a future test plan labeled passed. `subject_files` must cover the implementation/use-site attached to the proof, so changing the source invalidates the old claim.

The v3 CLI returns the computed verdict `DELIVERY_READY`, `INCOMPLETE`, or `BLOCKED`; exit 1 covers incomplete or blocked proof and exit 2 covers input/tooling errors. A missing browser is an honest incomplete visual gate, not permission to invent a passing record. Legacy commands may return `READY_FOR_REVIEW` only for legacy integrity checks.


## v2 execution pipeline

FRAME → NATIVE INVENTORY → PLATFORM CAPABILITY SCOUT → CONCEPT RETRIEVAL → REFERENCE DISCOVERY → DESIGN SYSTEM / PRECEDENT REVIEW → COMPONENT / ASSET SEARCH → DIRECTION → CRAFT CONTRACT → VERTICAL SLICE → MOTION / 3D PASS → RESPONSIVE PASS → CRAFT REVIEW → COMPONENT REPLACEMENT CHECK → RENDER MATRIX → REPAIR → DELIVERY RECEIPT.

The stage table above defines ownership; this sequence defines the v2 handoffs. Use [research-contract.md](research-contract.md) for v2 records and commands. Keep Sifr/Orun authority, native-first inventory, real-source acquisition, use-site proof, hashes and access-limit honesty. Search is mandatory for substantial work and the listed expressive triggers, including when native code exists: assess whether it meets the visual goal and compare relevant external precedent before deciding.

Normalize acquired tokens, radii, spacing, type, icon language, motion durations/easing/springs/stagger, responsive behavior, content, state, accessibility and theme. Preserve the defining source mechanism. Source acquisition is not permission to ship its unmodified demo defaults.

The delivery-receipt section above describes the preserved legacy core. New substantial work uses lobster-receipt/v3 and all applicable research/craft extensions. A legacy READY_FOR_REVIEW only reports legacy record integrity.


## Platform capability decision

Before choosing motion, scroll or positioning dependencies, read [platform-capability-scout.md](platform-capability-scout.md). Inspect current browser mechanisms, exact target support and fallback. Record native/hybrid/library choice with cost and behavioral reasons. The platform survey complements visual research; it does not count as acquired component provenance. New applicable deliveries attach platform_scout to receipt v3 and run verify-v3 with --require-platform where supported.

