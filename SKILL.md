---
name: plief-lobster
description: Coordinate frontend creation, redesign, and repair through Sifr design concepts, Orun real component acquisition, implementation, and rendered proof. Use for pages, product UI, visual direction, reference research, motion, scroll, typography, 3D craft, anti-slop repair, and requests to use actual library components; scale down for local UI edits.
license: Apache-2.0
---

# Pli'ef Lobster v2 — Hypercraft & Reference Acquisition

## v3 closed loop

Substantial work uses the closed verification loop: auto-profile the surface, run the platform scout, create a scenario matrix, execute a real browser adapter, inspect runtime mechanics, bind evidence to owners and dependency fingerprints, run a blind craft review, repair by root cause, rerun impacted scenarios, and issue a staged v3 verdict. A written receipt cannot claim execution truth. Read [runtime-proof](references/runtime-proof.md), [interaction-craft](references/interaction-craft.md), and [responsive-craft](references/responsive-craft.md) when routed by the profile.

Use `profile` and `plan` before loading every domain reference. Use `verify-v3` for the indexed receipt. Browser adapters may return `UNAVAILABLE`; that is an incomplete execution gate, not a pass.

## v3.1 proof authority

Receipt `stages` and `verdict` are cache/output only. The verifier ignores them and computes stages from validated child artifact content. `DELIVERY_READY` is a derived verdict, never an input stage. Empty or hash-valid garbage artifacts fail semantic validation. Runtime evidence must contain runner attestation, scenario results and current fingerprints. Scenario matrices are a closed protocol of typed actions/assertions; they cannot contain arbitrary JavaScript.

**Do not begin from invention when high-quality precedent, primitives, components, motion systems, shaders, models, typography systems, or design-system references can be inspected first. Research is part of implementation.**

**For substantial frontend work, external visual and component research is expected, not exceptional.**

For substantial frontend creation or redesign, do not default to hand-building commodity or expressive components before searching the project, configured registries, Orun sources, and relevant current external catalogs. Search is part of the design process.

A component catalog that is never queried provides no value. When a real component or reference could materially improve the result, actively inspect it.

Close the gap between a design concept, a component recommendation, and a working interface. The deliverable is the implemented experience. A named concept, search result, installed package, or screenshot alone does not demonstrate completion.

Ambition means a committed composition, useful behavior, and precise execution. It does not mean adding effects or dependencies to every surface.

## Language

Talk to the user in the user's language. **Write code in English.** These are different decisions and a request written in Portuguese, Spanish, French or any other language never changes the second one.

English applies to every identifier the codebase carries: variables, functions, components, hooks, types, interfaces, constants, enum members, CSS class names and custom properties, file and directory names, test names, branch names and commit messages, plus code comments and JSDoc. `useReducedMotion`, not `usePreferenciaDeMovimentoReduzido`. `SHAPE_PATHS`, not `CAMINHOS_DAS_FORMAS`. `ShapeDemo`, not `FormaDemo`.

The exception is content, not code: user-facing copy — labels, headings, button text, empty states, error messages, `alt` text, metadata — is written in whatever language the product serves, and that is usually the user's. In an internationalized project the keys stay English and the translated strings live in the locale files. Domain vocabulary with no accepted English equivalent (a legal or fiscal term such as `cpf`, `nfe`, `pix`) stays in its original form; it is a proper noun, not a translation failure.

When editing an existing codebase, match what is already there. A project whose identifiers are consistently in another language is not corrected as a side effect of an unrelated task — mixing two languages in one file is worse than either language used consistently. Say so and let the user decide.

## Ownership and entry

Lobster coordinates the workflow. Optional Sifr and Orun integrations are described by the local contracts [sifr](integrations/sifr.json) and [orun](integrations/orun.json). They are cooperating stages, not requirements of the distributed ZIP. Resolve them through explicit overrides, host configuration, registered installations, and only then a development fallback. Never invent a public URL.

For substantive frontend work, load Sifr and its routed modules. If a companion is absent, report it; continue available native and external research using these contracts, without claiming sibling retrieval or validation ran. Load Orun when choosing or integrating a capability, when the user requests actual provider components, or when native components cannot meet the requirement. Do not recursively reload Lobster from a sibling already working under this workflow.

| Request | Route and stopping point |
| --- | --- |
| New surface or substantial redesign | Frame → inventory → concepts → research → direction/craft contract → acquire → vertical slice → craft passes → render/repair → receipt v3 |
| Existing interface feels generic | Inspect render → identify structural/design cause → repair affected stages → render again |
| Add a named real component | Inspect native slot → Orun source verification → acquire source/package → mount and wire → exercise behavior |
| Audit or concepts only | Produce evidence-backed critique or distinct directions; preserve the requested read-only scope |
| Local copy, spacing, or defect fix | Inspect owner → narrow edit → relevant check; do not create a full artifact set or browse component galleries |

Read [the execution contract](references/execution.md) for new surfaces, redesigns, and component integration. Read [the craft review](references/craft-review.md) immediately before implementation and during visual review. Maintenance tests live in [behavioral cases](evals/cases/lobster-cases.json); do not preload them during UI work.

Domain routing: dense data → data-interface-craft; forms → form-craft; navigation → navigation-craft; editor → editor-craft; charts/maps → visualization-craft; media/image hero → media-craft; accessibility-critical interaction → accessibility-craft; substantial responsive work → responsive-craft; interactive UI → interaction-craft. Load only applicable modules.

## Craft routing

After native inventory, run the [Platform Capability Scout](references/platform-capability-scout.md) for substantial work and proposed motion/scroll/positioning dependencies. Compare current browser APIs with project mechanisms and libraries before acquiring. Check exact subfeatures, browser targets, support evidence, cost and fallback; choose native, hybrid or library with a concrete reason. Native browser geometry does not replace accessible interaction semantics. Attach platform-scout.json to the receipt and run verify with `--require-platform` for applicable work.

For substantial work read [research-contract](references/research-contract.md) and [reference-fabric](references/reference-fabric.md). Inspect at least three relevant external sources, retain candidate decisions, and make selected references change implementation. Visually important work spans structural, expressive, motion/3D and visual/design-system sources. Local copy/spacing repairs keep the narrow route.

Read [typography-craft](references/typography-craft.md) for role/face selection or type repair; [motion-craft](references/motion-craft.md) for animations and transitions; [scroll-craft](references/scroll-craft.md) for scroll changes; [3d-craft](references/3d-craft.md) for 3D/WebGL; [material-craft](references/material-craft.md) for glass, blur and effects. Load only applicable domains.

Before implementation, commit a craft contract in DNA: composition, type, spacing, material, motion, corners, icons, image/3D, scroll, primary expressive mechanism and effects budget. Preserve robust structural behavior while adapting expressive parts. After the vertical slice, check whether a stronger real component should replace commodity/custom work; integrate it, explicitly reject it, or retain a concrete implementation reference.

Review implementation correctness, integration correctness, visual craft, motion craft and 3D craft independently. A working feature cannot waive poor craft. Score required dimensions qualitatively out of five with observed evidence; any central score <=2 triggers repair, with no average-based shipping gate. Final rendered inspection remains necessary.

## 1. Establish what this surface must do

Inspect the target route, current render when available, real content, assets, package manager, installed primitives, styles/tokens, and relevant project instructions. Missing DESIGN.md does not make an existing interface a blank canvas.

State who arrives, the primary task, the content or proof they need, and the binding constraints. Distinguish the surface's purpose: persuade a decision, operate a task, support reading, or exhibit the work. A product can contain all four; its dashboard and landing page need different compositions.

Decide whether to preserve, extend, or replace the visual identity from the user's request and existing evidence. Preserve factual claims and working behavior during redesign. Ask only about missing information that would materially change the work; otherwise state reasonable assumptions and continue. Do not insert a mandatory approval round into an already authorized build.

## 2. Make concepts change the implementation

For new visual direction, execute Sifr concept retrieval when the resolver reports it available; otherwise record concept-engine unavailability and continue with the generic research contract when allowed. Use product/job/content terms; add English search terms when helpful because the local index tokenizes English vocabulary. Do not conclude that a Portuguese request has no applicable concept after one literal empty search.

The bundled discovery helper calls an AVAILABLE resolved integration and retains its response; absent integrations return `UNAVAILABLE`:

```text
python "<lobster-dir>/scripts/lobster.py" discover --concept "archive editorial reading hierarchy" --out "<project>/.plif/artifacts/<surface-id>/discovery.json"
python "<lobster-dir>/scripts/lobster.py" discover --capability "accessible command menu keyboard search" --framework React --out "<project>/.plif/artifacts/<surface-id>/component-discovery.json"
```

Replace example queries with the actual need. The helper performs local retrieval, not native inspection, live verification, or installation. A returned framework match or ranking score is a lead, not a passed compatibility gate.

Read two to four relevant concept records and their tensions. Choose one dominant grammar with bounded support. In Sifr's DesignDNA, connect at least three consequential laws to product needs: composition, typography, information density, material, interaction, or motion. For each law identify the component/token it changes and the rendered observation that will demonstrate it. Reject conflicting rules explicitly. A list of style adjectives does not pass this stage.

When direction is materially open, compare two credible compositions with the same content, task, and states. Differences must affect topology, hierarchy, or interaction, not only colors. Render comparisons when available. If the brief already pins the concept, execute that concept faithfully rather than replacing it with your taste. Keep decision artifacts out of shipped UI, hidden DOM, and client bundles.

## 3. Turn Orun discovery into an actual part

Inspect project-native components first and record their fit. When external acquisition is warranted, fill and validate Sifr's Orun query using actual project facts; never retain the template's example framework, budget, candidate, or evidence URL.

Execute capability retrieval, inspect the current official source for the shortlisted part, and select against hard stack, license, behavior, accessibility, and cost constraints. A provider gallery or screenshot is visual evidence, not source code. Record why reuse, adaptation, composition, or custom implementation wins.

For a selected external component, the acquisition is incomplete until the real package or licensed source exists in the project, its API is inspected, it is used by the target route, and its meaningful behavior is exercised. Preserve the useful source mechanism while adapting demo tokens, copy, routes, icons, and state to the chosen world.

Never hand-write a generic substitute and call it a Magic UI, shadcn, Aceternity, or other provider component. If source is unavailable or incompatible, identify that gap and choose an explicit fallback. When the user specifically requires external components, that requirement remains unresolved until a real one is integrated or the user changes it. Custom work can still be the correct outcome when it is not a silent substitution.

## 4. Prove a vertical slice before multiplying it

Implement the defining section and one real interaction first. Use real or honestly labeled representative content. Connect one selected part to the actual route and existing state. Render at a wide and narrow width, exercise the primary interaction, and compare the result against the concept laws before repeating the pattern throughout the application.

Then complete the requested flow: navigation, actions, loading, empty, error, success, keyboard, touch, and relevant data extremes. Use existing production boundaries; label simulation honestly when building a prototype. An impressive first viewport with dead controls is unfinished.

Validate Sifr artifacts with the resolved integration's declared interface. If Sifr is unavailable, mark the concept pass unavailable instead of claiming validation.

## 5. Inspect the result, repair the cause

Run technical checks appropriate to the change and the repository. Batch screenshots and interaction evidence for representative widths and states. Review the product task and concept fidelity before cosmetic defect lists. Classify issues by owner: structure, concept, source integration, behavior, content, accessibility, responsiveness, or runtime.

Repair together, then inspect the affected matrix again. After two passes with the same unresolved defect, change the diagnosis or implementation approach rather than polishing around it. This bounds repetitive work, not permission to ship a known material defect. Stop adding discretionary polish once the requested experience works and the evidence is sufficient.

For substantive builds, complete the [delivery receipt](references/execution.md#delivery-receipt) beside Sifr's artifacts and run:

```text
python "<lobster-dir>/scripts/lobster.py" verify "<project>/.plif/artifacts/<surface-id>/lobster-receipt.json" --project "<project>"
```

This checks required records, existing files, and content hashes. It does not execute the UI or certify aesthetics, accessibility, provenance authenticity, or component use. Review those against the actual code and browser evidence. `DELIVERY_READY` is computed only by `verify-v3`; legacy `READY_FOR_REVIEW` is retained for v1/v2 compatibility.

## Completion

Report the delivered surface, concept laws visible in it, actual components integrated with source and adaptation, checks run, and remaining gaps. Separate implemented, rendered, and behavior-tested claims. Missing browser capability leaves rendered review unverified; finish available implementation and checks without fabricating screenshots or calling source inspection visual proof.

The workflow is adapted from [Impeccable](https://github.com/pbakaus/impeccable) and integrated with this repository's Sifr/Orun contracts. See [NOTICE](NOTICE.md) for the pinned source and adaptation boundaries.


> **The goal is not to demonstrate that the agent can implement every visual mechanism from scratch. The goal is to ship the strongest coherent interface available within the user's constraints. Use the web, registries, design systems, component catalogs, motion libraries, 3D ecosystems, and existing project primitives as active design material. Research deeply, acquire honestly, adapt deliberately, and reject mediocre craft even when the code technically works.**



> **Do not let useful references remain decorative documentation. If they can materially improve the result, search them.**
