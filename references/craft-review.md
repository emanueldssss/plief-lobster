# Craft review

Adapted from Impeccable's surface modes, craft floor, and design critique. Apply against the actual brief and rendered work. A user's explicit aesthetic remains authoritative; pattern warnings are diagnostic prompts, not universal bans on fonts, cards, gradients, or color.

## Review the concept before the finish

1. **Task:** Can the intended person find and complete the primary action? Does the first viewport contain the right evidence, controls, or artifact for this surface?
2. **Composition:** Does the silhouette follow the chosen concept? Inspect region proportions, anchor, reading path, density, grouping, and responsive transformation. Neutralize accent/effects mentally or in a reversible preview; identity should survive in the meaningful relationships.
3. **Specificity:** Could an unrelated product use the same page by replacing its name? Identify the real content, interaction, or composition that makes this one specific. Shared conventions remain useful in operating UI; do not sacrifice recognition to pass a novelty test.
4. **Parts:** Locate each selected component in the live flow. Test what justified choosing it: keyboard navigation, sorting, disclosure, motion response, focus restore, or another concrete behavior. Removing the mechanism while retaining a wrapper does not fulfill the selection.
5. **Finish:** Review type, spacing, color, assets, motion, copy, states, and edge conditions together. Pretty pixels cannot compensate for the earlier failures.

## Common failures and the repair owner

| Observed failure | Diagnose before editing | Root repair |
| --- | --- | --- |
| Every section is the same icon/card grid | Is unrelated information being forced into one container? | Recompose by content relationship: list, table, comparison, sequence, document, workspace, or image field |
| Huge heading and empty hero for an operational tool | Is a persuasion scaffold hiding the task? | Put task and status in the initial working area |
| Concept name exists only in the brief | Which promised law has no source owner or visible consequence? | Materialize the law in structure, typography, behavior, and states |
| Real component installed but interface unchanged | Is it reachable, instantiated, and connected to actual state? | Integrate the selected mechanism in the target route |
| Many attractive parts look unrelated | Are demo tokens, radii, icons, typography, or animation engines competing? | Adapt all parts to the dominant grammar and host contracts |
| Purple gradients removed but layout still generic | Did the work change only a saturated aesthetic? | Revisit content hierarchy and product-specific composition |
| Desktop screenshot works; narrow screen collapses | Was width reduction substituted for structural adaptation? | Change grouping, navigation, order, and density at the responsible region |
| Controls are decorative | Are actions unimplemented or simulation boundaries hidden? | Connect handlers/state and verify outcomes; label prototype boundaries |

## Typography, color, assets, motion

Typography needs distinct roles, readable measure, deliberate scale, and resilient wrapping with real copy. Use tabular numerals where comparison benefits. Test long labels, translated text where supported, zoom, and fallback fonts. Do not add an exotic typeface when the committed concept or task calls for the native system.

Color has semantic and hierarchical roles. Measure contrast on the actual surface, including focus, disabled/non-text cues where applicable, imagery, transparency, and dynamic backgrounds. Do not communicate status by color alone. Shadows and materials must agree about depth; avoid accumulating unrelated glow, glass, grain, and elevation as hierarchy substitutes.

Assets must earn their area by evidence, explanation, or a stated experiential role. Use real supplied assets, licensed sources, or appropriately generated assets when available and useful. Keep a coherent crop, lighting, scale, and treatment. Do not invent customers, performance claims, prices, testimonials, or product capabilities. Label illustrative data where it could be mistaken for fact.

Motion should explain causality, spatial relationships, progress, or a specific expressive moment. A small motif system beats entrances on every section. Preserve interruption and reduced-motion behavior; essential content must remain available when animation or heavier media fails. Do not add WebGL to satisfy a request for “better design” without a product role and budget.

## Render matrix

Choose representative widths from the actual responsive contract. Include a narrow phone, a wide desktop, and the transition width most likely to break. Add tablet, touch, reduced motion, theme, or device conditions when they exercise distinct behavior. Capture loading/empty/error/overflow and overlay states relevant to the changed flow.

Check primary action, navigation, keyboard sequence, visible focus, overlay dismissal/focus return, and a realistic content extreme. Compare source/runtime errors and layout measurements with screenshot inspection. Do not claim accessible from a single automated score or fast from a clean build.

Each material finding needs location/state, observed failure, user consequence, owner, and a correction criterion. Keep the strongest concern even when the interface looks impressive. Fix the owner and re-render affected cases; avoid endless global restyling.

## Final judgment

Answer with evidence: Does the interface perform its job? Are the selected laws visible? Are the promised real parts used and working? Are known material defects resolved? What remains unverified?

A deterministic receipt or detector can reject missing evidence and mechanical defects. It cannot certify beauty, specificity, coherent concept execution, or an honest causal relationship between product and design. Those require inspection of the finished experience.


## v2 craft obligations

Use [research-contract.md](research-contract.md) for scorecard fields and independent gates. Review screenshots for observed quality; existence is insufficient. Motion needs temporal evidence, 3D needs its dedicated observations. Qualitative scores never replace observation or average away a central defect.


## Craft Scorecard

Aplicar ao review uma scorecard qualitativa obrigatória.

```text
Composition         /5
Typography          /5
Spacing             /5
Color               /5
Material            /5
Component coherence /5
Motion              /5
Interaction         /5
Responsiveness      /5
Accessibility       /5
Performance         /5
Specificity         /5
```

Se houver 3D:

```text
Geometry            /5
Materials           /5
Lighting            /5
Camera               /5
Rendering fidelity  /5
3D performance      /5
```

Não usar média matemática como shipping gate.

Qualquer:

```text
<= 2
```

em dimensão central ao conceito gera repair pass.


## Screenshot Review Enhancement

Em cada screenshot, inspecionar explicitamente:

```text
silhouette
hierarchy
alignment
density
type rendering
edge quality
blur quality
shadow quality
asset resolution
animation resting states
visual noise
contrast
component consistency
```

Para 3D:

```text
aliasing
texture resolution
lighting
material response
camera framing
model silhouette
```


## Motion Evidence

O receipt registra:

```text
motion_evidence
```

Não apenas screenshot.

Pode incluir:

```text
trace
recording
frame sequence
interaction observation
```

Registrar:

```text
trigger
from
to
duration/easing mechanism
interruption behavior
reduced-motion behavior
```


## Craft Repair Loop

Quando o usuário disser:

```text
porco
genérico
barato
low quality
sem resolução
AI-looking
```

Lobster não deve fazer apenas:

```text
increase blur
increase shadows
add animation
```

Diagnosticar em dimensões:

```text
composition
type
asset resolution
model quality
lighting
material
motion
timing
spacing
density
source component quality
integration quality
```


## “AI-looking” Detector

Sinais:

```text
same radius everywhere
same card everywhere
all sections centered
huge headings
gradient text
purple glow
floating blobs
generic icon + title + paragraph
every entrance fade-up
identical spacing
glass everywhere
overused bento
random grain
random marquee
default Lucide in every block
```

Não banir.

Detectar uso automático.


## Detail Pass

Antes do final render:

```text
pixel-level alignment
baseline alignment
icon optical sizing
border opacity
shadow falloff
gradient banding
text antialiasing
image crop
hover timing
focus transition
sticky edges
scrollbar
selection state
empty state
loading state
```
