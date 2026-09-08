# Research and craft record contracts

## Search before implementation

For substantial frontend creation or redesign, research is mandatory. Inspect native inventory, current configured registries, Orun and relevant external catalogs before hand-building commodity or expressive parts. Research is also required for the expressive/motion/3D triggers below, even without a named library. A narrow label/spacing correction keeps the narrow route.

Inspect at least 3 relevant external sources; 5–8 is recommended when useful. For visually important work, cover a structural source, an expressive source, a behavior/motion/3D source and a visual/design-system reference. Sources can overlap classes, but depth and diversity require reviewer inspection. Duplicate pages are not independent sources. Tool/access constraints remain an explicit unmet gate; never fill fictional research to reach a quota.

Derive queries along product task, visual grammar, interaction and implementation mechanism. Prefer “editorial horizontal index navigation” or “cinematic product camera scroll” to “nice card”. Retain exact queries, inspected item, observed mechanism, selection/rejection reason and captured inspection record. A consulted reference must change implementation or have an explicit rejection; superior candidates cannot disappear. Custom wins only for demonstrated fit, cost, preserved behavior or absence of a credible source. Novelty is not measured by how much code was written locally.

## CLI

From the skill folder, create a draft outside public assets:

```sh
python scripts/lobster.py research --need "cinematic 3D product hero" --framework React --categories components,motion,3d --out reference-search.json
python scripts/lobster.py research-verify reference-search.json --project . --expressive
python scripts/lobster.py craft-check lobster-receipt.json --project .
python scripts/lobster.py verify lobster-receipt.json --project .
```

`research` creates empty arrays and reports DRAFT/research_performed=false; it performs no search and refuses to overwrite existing evidence. Populate it using actual host searches and set research_performed=true only after inspection. The empty draft correctly fails research-verify. Exit 0 means draft created or records ready for review, 1 means incomplete and 2 means inspection/input error. `craft-check` checks craft records; `verify` is the combined implementation + research + craft gate. Neither executes a browser or judges aesthetics.

## reference-search.json

Schema `lobster-research/v1`:

- `need`: actual product need; `framework` and `categories`: search context; `queries`: nonempty strings.
- `sources`: nonempty objects with unique `name`, HTTP(S) `url` without credentials, `category` array from the fabric, `access` (official/community/reference), `mode` (ACQUISITION/REFERENCE_ONLY/BOTH), `inspected: true`, concrete `observation`, and `evidence` file object.
- `candidates`: unique `name`, known `source`, item `url`, `mechanism` (visual), `interaction_mechanism`, `framework`, `stack_fit`, `license`, `dependencies` string array (may be empty), `bundle_implications`, `accessibility`, `adaptation_cost`, `status` (selected/rejected/reference), and `reason`. Every counted source needs a candidate; a rejected item may state unknown license as the reason for rejection. Selected items require an inspected license and acquisition-capable source. Reference-only inspection must never be recast as acquisition.
- `implementation_impacts`: one or more objects with active `candidate`, concrete `change`, `implementation` file object and `evidence_ids`. Every selected/reference candidate has an impact. In the combined receipt these IDs must resolve to current passed visual/interaction evidence covering the implementation owner. A rejected candidate cannot count as implementation impact.

All file objects contain project-relative `path` and SHA-256 `sha256` over actual bytes. Store inspection notes, captures or source metadata before hashing. Research-verify checks file integrity and records; authenticity, license truth, query relevance and visible impact require actual inspection. In combined verification each selected acquisition also matches an external `components` entry by exact item `source_url`, with the existing implementation/use-site/source-evidence requirements. For acquired assets, record their actual rendering wrapper and usage there. Reference-only adaptations retain status reference and never claim acquired source.

Extend the Orun selection record with `discovery: {sources_consulted, queries, candidate_count, shortlisted}` when its schema allows extensions. Otherwise keep that extension in reference-search.json beside the authoritative Orun record and cross-reference it; do not break a sibling schema. The source/candidate/impact arrays are canonical; selected/rejected/reference lists are projections, not competing copies.

## Receipt v2

Keep legacy fields from execution.md only when migrating old records. New records use `format: lobster-receipt/v3` and add:

- `profile`: explicit booleans `substantial`, `expressive`, `motion`, `3d`, `heavy_effects`, derived from the brief and implementation. Do not mark a central feature false to avoid evidence.
- `research`: `required` boolean, `artifact` file object, `sources_consulted` source names, `selected_references` names of selected/reference candidates, and `impact` change strings matching the research artifact. Research cannot be waived when substantial/expressive/motion/3d is true. Scoped exemptions require `reason`.
- `craft_contract`: nonempty strings `dominant_composition`, `type_system`, `spacing_rhythm`, `surface_material_model`, `motion_grammar`, `corner_language`, `icon_language`, `image_3d_treatment`, `scroll_behavior`, `primary_expressive_mechanism`, `effects_budget`. Summarize authoritative DNA; justify absence where a feature is intentionally unused.
- `craft_scorecard`: rows with `dimension`, integer `score` 1–5, `central` boolean, `observation`, and `evidence_ids`. Required dimensions: composition, typography, spacing, color, material, component_coherence, motion, interaction, responsiveness, accessibility, performance, specificity. Add geometry, materials, lighting, camera, rendering_fidelity, 3d_performance for 3D. Motion alone may have null score with reason when profile.motion=false. Name central dimensions honestly; central <=2 requires repair, never average it away.
- `craft_gates`: independent implementation, integration, visual, motion and 3d objects with `status`, `observation`, `evidence_ids`. Applicable gates must pass after actual observation. Implementation needs check evidence; visual needs visual evidence; integration/motion/3d need visual and interaction evidence. Inapplicable motion/3d use not_applicable and an observation explaining why. Failed/unverified gates remain incomplete.
- `motion_evidence`: rows with `trigger`, `from`, `to`, `duration_easing`, `interruption`, `reduced_motion`, `evidence_ids` to passed interaction observations. Capture a trace, recording, frame sequence or exercised interaction log. A still screenshot alone cannot demonstrate timing.
- `3d_evidence`: rows with `asset_source`, `model_format`, `texture_sizes`, `renderer_dpr`, `lighting`, `camera`, `performance_observation`, `mobile_fallback`, `evidence_ids` to visual and interaction observations. Values are descriptive strings including measured units and context.
- `performance_budget`: required for heavy effects or 3D; strings `js_cost`, `asset_weight`, `texture_memory`, `video`, `draw_calls`, `animation_work`, `layout_work`, `measured_result`, `fallback`, plus `evidence_ids` to check evidence. Compare observed cost against the agreed budget; justify unused dimensions.

Legacy v1 is still readable and returns a legacy contract annotation. It does not satisfy v3 substantial-work delivery. Migrate by performing research/reviews, recording their observations and hashing current artifacts; changing only the format string fails. File edits invalidate affected evidence, including research artifact and impact owners. Matching hashes attest consistency, not truth or completeness of the dependency graph.


## Mandatory Research Triggers

Pesquisa externa torna-se **obrigatória** quando o pedido contém ou implica:

```text
premium
beautiful
insane
cinematic
immersive
award-winning
experimental
editorial
interactive
3D
WebGL
shader
animation-heavy
motion-heavy
scroll experience
parallax
glass
blur
mesh
morph
text animation
creative landing page
portfolio
showcase
redesign
anti-slop
high fidelity
```

Também é obrigatória quando a primeira implementação proposta contém:

```text
custom animated hero
custom carousel
custom command menu
custom complex nav
custom marquee
custom scroll scene
custom shader
custom globe
custom 3D scene
custom text effect
custom animated background
custom modal choreography
```

Antes de implementar do zero, Lobster deve pesquisar se uma base de maior qualidade já existe.


## Anti-Component-Amnesia

Uma das falhas mais importantes a corrigir:

> A IA pesquisa componentes, encontra coisa boa e depois volta para o JSX genérico que ela inventaria de qualquer maneira.

Nova regra:

Quando um candidato externo for considerado superior:

```text
IT MUST EITHER
A. be integrated,
B. be explicitly rejected with reason,
C. become a concrete implementation reference.
```

Não pode simplesmente desaparecer do raciocínio operacional.


## Component Replacement Pass

Após o primeiro vertical slice:

Lobster deve perguntar internamente:

```text
Which hand-written parts are commodity implementations that could be replaced by a stronger real component?
```

Pesquisar novamente quando necessário.

Especialmente:

```text
menu
carousel
tabs
dialog
command palette
date picker
upload
tree
data table
gallery
dock
animated text
scroll effect
3D showcase
```


## Reference-Driven Creation

Mesmo quando nenhum componente é adquirido, referências devem influenciar implementação.

Formato:

```text
reference A
→ spatial principle

reference B
→ interaction pattern

reference C
→ type treatment

project DNA
→ adaptation
```

Isso cria design synthesis.

Não collage.


## Search Queries Must Be Visual

Evitar queries pobres:

```text
nice card
cool UI
modern website
```

Usar:

```text
editorial horizontal index navigation
cinematic product camera scroll
dense AI command center
elastic dock navigation dark interface
progressive blur image gallery
high contrast grotesk editorial landing
spatial card stack interaction
shader hero displacement monochrome
```


## Query Expansion

Sempre derivar múltiplos eixos:

```text
product task
visual grammar
interaction
implementation mechanism
```

Exemplo:

```text
AI editor
+
dense technical
+
command navigation
+
keyboard accessible command palette
```


