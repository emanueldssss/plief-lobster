# Platform Capability Scout

Run after project-native inventory and before choosing a dependency for motion, transitions, positioning or scrolling. Run for substantial creation/redesign and whenever the proposed implementation adds or replaces a library for a capability the platform may already provide. A label/spacing edit does not trigger a platform survey.

Inspect both native project code and native browser capabilities; these are different inventories. The goal is the strongest compatible mechanism within the product constraints. Prefer the platform when it provides the required behavior and craft at lower total cost. Keep a library when it supplies necessary orchestration, semantics, compatibility or integration already present. Do not remove working dependencies merely to improve a dependency count.

## Discovery and support

1. Read actual browser targets, embedded WebViews, device constraints, framework/router behavior and installed capabilities. Record exact minimum versions or the unresolved target-policy assumption. Never infer targets from your development browser.
2. Inspect current MDN compatibility data, web.dev Baseline and official browser/specification documentation for the exact subfeature. Record URLs, checked date and retained inspection evidence. Baseline describes interoperability across its browser set; Newly available is not Widely available and neither guarantees a particular audience, embedded browser, accessibility result or bug-free implementation. A specification or beta release is not stable support.
3. Compare platform, existing project mechanism and an appropriate library. Record behavioral gaps, total adaptation/maintenance cost, payload, browser coverage, accessibility, performance and fallback. Library use must have a concrete reason beyond habit; native use must have evidence beyond “modern browser”.
4. Select native, hybrid or library. Native enhancement must leave the primary task usable when unavailable. Hybrid must avoid running two competing animation/positioning systems on the same element. Do not install a polyfill automatically; compare its cost and fidelity with an existing library or simpler fallback.
5. Implement the actual chosen slot, then exercise supported and forced-unsupported paths, keyboard/touch, reduced motion, resize and relevant navigation interruption. Feature detection proves API exposure or syntax recognition, not correct behavior. Retain observed outcomes tied to current files.

## Capability leads

| Need | Inspect platform first | Keep a library when |
| --- | --- | --- |
| State/page continuity | Same-document `document.startViewTransition`; inspect cross-document `@view-transition` and any types/scoping separately | Router lifecycle, choreography, gestures or required target support need more |
| Scroll-linked progress/reveal | CSS `animation-timeline`, `scroll()` / `view()` and exact range/axis support | Complex sequencing, pinning, scrubbing or compatibility cannot meet the contract |
| Floating element placement | CSS Anchor Positioning, exact `anchor-name`, `position-anchor`, `anchor()` and position-try features | Collision strategy, portal/virtual anchors, transforms or browser targets require a positioning engine |
| Simple temporal animation | CSS transitions/keyframes or Web Animations API | Authored timelines, shared state, springs or gesture composition justify orchestration |

Anchor positioning handles geometry. It does not implement a combobox/menu's keyboard model, semantics, focus return, dismissal or labeling. Inspect native dialog/popover separately when appropriate; preserve existing accessible primitives. The same-document View Transition capability does not prove cross-document, scoped or experimental extension support.

For native view transitions, ensure the underlying state update runs with no transition API and with reduced motion; test interruption and focus/scroll restoration. For scroll animations, preserve visible content and native input in the fallback; use guarded CSS and inspect actual compositor/layout work. For anchors, feature-detect every property/function used and test overflow, scroll containers, zoom, resize, touch and top-layer/portal interactions.

## Current reference checkpoint

Inspected 2026-09-07; refresh at use, not by trusting this date indefinitely:

- [web.dev January 2026](https://web.dev/blog/web-platform-01-2026?hl=en): Anchor Positioning reached Baseline Newly available with Firefox 147. Do not extend this claim to every later anchor subfeature.
- [MDN View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API): inspect same-document and cross-document features independently.
- [MDN animation-timeline](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timeline) and [anchor-name](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/anchor-name): inspect the compatibility table for each mechanism actually used.
- [Baseline definition](https://web.dev/baseline): distinguish availability levels from the project's support policy.

## Evidence contract

Store `.plif/artifacts/<surface-id>/platform-scout.json` with `schema: lobster-platform/v1`, `target_browsers` (nonempty strings), `checked_at` (ISO date), and `decisions` (nonempty objects):

- `capability`: exact feature/subfeature, unique within the record.
- `choice`: native, hybrid or library.
- `native_option`, `library_option`, `reason`, `support_observation`, `feature_detection`, `fallback`, `accessibility`, `cost_comparison`: nonempty observations. Explain if no credible library is relevant.
- `support_urls`: current official compatibility/documentation URLs; `support_evidence`: project-relative path/sha256 object containing the retained inspection.
- `implementation`: current path/sha256 object for the owner.
- `evidence_ids`: passed receipt visual/interaction evidence covering that owner, including actual chosen behavior.
- `fallback_evidence_ids`: passed interaction evidence covering that owner, observing the forced-unsupported path or library fallback and essential behavior. A fallback plan is not a passing observation.

Attach the artifact to receipt v2 as `platform_scout: {path, sha256}`. New applicable work runs:

```sh
python scripts/lobster.py verify lobster-receipt.json --project . --require-platform
```

The flag rejects missing Scout evidence and works with the existing v2 gates. Without it, legacy receipts remain readable; an attached Scout is still validated. The CLI checks record/file consistency, not browser execution, the truth of support claims or freshness relative to an invented expiration interval. Reinspect when targets, chosen APIs or support facts change. The Scout complements external visual/component research; it does not waive reference diversity or provenance.
