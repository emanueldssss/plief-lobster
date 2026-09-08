# 🦞 Pli'ef Lobster v2 — Hypercraft & Reference Acquisition

[![skills.sh](https://skills.sh/b/emanueldssss/plief-lobster)](https://skills.sh/emanueldssss/plief-lobster)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Version](https://img.shields.io/badge/version-2.1.0-orange)

**Agent skill that turns "vibe-coded UI" into researched, acquired, craft-reviewed frontend.**

Lobster coordinates frontend creation, redesign, and repair. It makes external **research mandatory** for substantial work, tracks every reference as **hashed evidence**, forces **real component acquisition** (no fake "I used shadcn" claims), and runs an **independent craft review** across visual, motion, 3D, scroll, material, and typography dimensions before anything is called done.

```
┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌─────────┐
│  Frame  │ → │ Concepts │ → │ Research│ → │  Acquire │ → │  Vertical │ → │  Craft  │
│ purpose │   │  (Sifr)  │   │REQUIRED │   │   real   │   │   slice   │   │ review  │
└─────────┘   └──────────┘   └─────────┘   └──────────┘   └───────────┘   └─────────┘
                                                                    ↓
                                                             Receipt v2 + verify
```

## Why

LLM agents hand-roll commodity components, ignore the ecosystem, claim integrations that never happened, and ship screenshots as "proof". Lobster fixes this structurally:

- **Research is not optional.** A receipt that waives external research is rejected.
- **References must change the implementation.** Every source records an impact owner and evidence. Decorative "we looked at Awwwards" doesn't pass.
- **Acquisition is real.** A "Magic UI component" only counts when the actual package/source exists in the project, its API was inspected, and its behavior was exercised. Hand-written substitutes are flagged.
- **Craft review is independent.** Five dimensions scored with observed evidence — no averaging a broken gate into a pass.
- **Nothing ships without a receipt.** `lobster-receipt/v2` with file hashes, verified by CLI.

## Install

### Via [skills.sh](https://skills.sh) — any agent, one command

```bash
npx skills add emanueldssss/plief-lobster
```

Targets Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot, Windsurf and [70+ more](https://skills.sh). Add `-g` for global, `-a claude-code` to pin an agent.

### Via npm (CLI access)

```bash
npm install -g plief-lobster
lobster --help
```

### Via git

```bash
git clone https://github.com/emanueldssss/plief-lobster.git
python plief-lobster/scripts/lobster.py --help
```

**Requirements:** Python 3.10+ (stdlib only — zero dependencies). Skills host loads `SKILL.md`; browser/render capabilities belong to the host.

## The CLI

```bash
python scripts/lobster.py <command>            # or: lobster <command>
```

| Command | What it does |
| --- | --- |
| `discover` | Queries Sifr (design concepts) + Orun (components) local engines in parallel. **Local index only** — a match is a lead, not a compatibility gate. |
| `research` | Creates an unverified research draft that the host fills with real searches. Intentionally incomplete until filled. Refuses overwrite. |
| `research-verify` | Validates the research record: breadth, diversity, impact linkage, no unsafe paths / credential URLs, no waived research. |
| `craft-check` | Validates the independent craft scorecard: five gates, evidence per dimension, no still-frame passing as motion evidence. |
| `verify` | Validates the delivery receipt: required records, existing files, **SHA-256 integrity**, project-relative paths, no traversal. `--require-platform` additionally demands the Platform Capability Scout record. |

```bash
# Example: validate a delivery receipt
python scripts/lobster.py verify .plif/artifacts/landing/lobster-receipt.json --project .
```

Exit codes: `0` ready · `1` incomplete · `2` inspection error.

## Workflow (what the skill enforces)

1. **Establish purpose** — who arrives, primary task, persuade/operate/read/exhibit.
2. **Concepts change implementation** — Sifr retrieval, ≥3 DesignDNA laws connected to product needs, each with a rendered observation that will prove it.
3. **Research the fabric** — ≥3 external sources inspected (Open Props, design systems, component registries, motion/3D catalogs), candidates retained with hashed evidence.
4. **Acquire for real** — inspect native slot first; external component isn't "used" until package/source exists, API inspected, mounted, behavior exercised.
5. **Vertical slice first** — defining section + one real interaction at wide/narrow widths before multiplying.
6. **Independent craft review** — implementation, integration, visual, motion, 3D scored 0–5 with evidence; any central gate ≤2 blocks shipping.
7. **Receipt v2** — CLI-verified integrity. `READY_FOR_REVIEW` = document integrity, not a shipping verdict.

## What's new in v2.1 — Platform Capability Scout

- **Scout before dependencies.** For motion, scroll and layout capabilities, the agent compares **native browser APIs, hybrid approaches, and libraries per subfeature** — recording exact browser targets, support inspection, cost, accessibility, and an *exercised* fallback (no still-frame pretending to be temporal evidence).
- **`verify --require-platform`** — enforcement flag: applicable new work must carry a platform record. Attached platform evidence is always validated, flag or not; older v2 receipts remain readable.
- **L-21–24** behavioral cases + 7 platform regression tests (55 total).
- Fixed a UTF-8/Windows decoding corruption in eval case L-12.

### What was new in v2

- **Mandatory retained research** — receipt v2 rejects waived research for substantial work
- **Reference acquisition contracts** — Open Props, VibePrompt, ReUI, DesignSystems.one, 21st.dev, shadcn registries, Aceternity, Magic UI, React Bits, headless primitives
- **New craft domains** — 3D (model/material/texture/render split), motion, scroll, typography, material/blur contracts
- **Anti-amnesia** — every component has a destiny and impact; no orphan references
- **Temporal evidence gates** — still frames can't pass motion; screenshots can't pass 3D
- **New commands** — `research`, `research-verify`, `craft-check`

Full validation reports: [`docs/VALIDACAO-V2.1.md`](docs/VALIDACAO-V2.1.md) · [`docs/VALIDACAO-V2.md`](docs/VALIDACAO-V2.md)

## Companions (optional)

Lobster is the orchestrator. Siblings unlock extra powers but are **not required**:

| Sibling | Owns | Without it |
| --- | --- | --- |
| `plief-sifr` | Product framing, DesignDNA, concept retrieval | Native/external research still works |
| `plief-orun` | Component discovery + provenance | External catalogs still work |

Drop them as sibling folders for local discovery; missing companions are reported as `ERROR` by `discover`, never silently skipped.

## Development

```bash
python -m unittest discover -s tests -v   # 55 cases
```

The v1 receipt format remains readable for legacy validation, but substantial builds require v2 gates. Migration guide: [`references/research-contract.md`](references/research-contract.md).

## Credits & License

Apache-2.0. Workflow adapted from [Impeccable](https://github.com/pbakaus/impeccable) by pbakaus and contributors — see [NOTICE.md](NOTICE.md) for pinned source (`831cabe`) and adaptation boundaries.
