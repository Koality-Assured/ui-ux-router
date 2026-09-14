---
doc_kind: requirement
canonical_id: ui-ux-overlay
purpose: [requirement]
rank: high
topics: [ui-ux, overlay, design-tokens, a11y, visual-regression]
rag_keywords: [ui-ux, domain-overlay, spoke, wcag, dtcg, playwright]
---

# ui-ux domain overlay

Spoke-local UI/UX pack for `Koality-Assured/ui-ux-router`. Generic machinery stays in `ai-harness-core`. Do not copy this overlay, instance `projects/`, `research/`, or `ai-tooling/memory/` back to core. Do not dump this pack into `ai-router`.

Pull core updates: `python scripts/sync/pull_harness_core.py --dry-run --json`.
Propose generic core changes: `python scripts/sync/propose_core_update.py --dry-run --json`.

## Domain specialists (criterion 5)

| Agent | Tier | Owns |
| --- | --- | --- |
| [`design-system-architect`](../../ai-tooling/agents/design-system-architect/AGENT.md) | high | `design-token-manage` |
| [`a11y-compliance-operator`](../../ai-tooling/agents/a11y-compliance-operator/AGENT.md) | standard | `wcag-accessibility-audit` |
| [`visual-qa-operator`](../../ai-tooling/agents/visual-qa-operator/AGENT.md) | standard | `visual-regression-audit` |
| [`interaction-designer`](../../ai-tooling/agents/interaction-designer/AGENT.md) | standard | `responsive-breakpoint-verify` |

Skills live under `ai-tooling/skills/ui-ux/<name>/SKILL.md`.

## Scripts and fixtures

- `python scripts/ui-ux/run_visual_regression.py` — synthetic (default) or Playwright goldens at 375/768/1280/1920.
- `python scripts/ui-ux/audit_accessibility.py` — planted contrast, keyboard-trap, unlabeled, target-size; optional axe-core.
- `python scripts/ui-ux/compile_design_tokens.py` — DTCG `$value`/`$type` lint + CSS/SCSS/Tailwind.
- Fixtures: `scripts/ui-ux/fixtures/components/` (buttons, modal, form). Goldens: `scripts/ui-ux/fixtures/baselines/`. Tokens: `scripts/ui-ux/fixtures/tokens/tokens.json`.

Synthetic components only. Do not vendor Distastefu1/secpanic-idler or other product UI.

## Gates

- Default visual engine is OS-stable synthetic raster. Playwright goldens are environment-specific.
- Axe/stdlib findings are not WCAG certification.
- Token files MUST NOT mix legacy `value` with DTCG `$value`.
