---
schema_version: "2.0.0"
name: visual-regression-audit
description: >-
  Compare frozen-motion screenshots of synthetic UI fixtures against golden PNGs at 375/768/1280/1920 CSS pixels. Use when the user asks for visual regression, screenshot gates, or pixel diff. Do not use for WCAG audits (wcag-accessibility-audit) or token compile (design-token-manage).
owner_agent: visual-qa-operator
rank: high
isolation: mutate
on_failure: abort_and_rollback
prerequisites:
  - python
dependencies:
  required_skills:
    - isolate-work
  delegated_skills: []
  in_session_skills: []
contracts:
  inputs:
  - Fixture set, viewport list, engine (synthetic default or playwright), and update-baselines authorization
  outputs:
  - Pass/fail report with diff_pixels per fixture/viewport, and updated goldens only when authorized
topics: [ui-ux, visual-regression, playwright]
routing_hints: [screenshot, golden, pixel-diff]
---

# Visual regression audit

## When to use

Pixel comparison against committed goldens, first-run baseline writes, or CI screenshot gates on synthetic components.

## When not to use

Accessibility rule runs (`wcag-accessibility-audit`). Token lint (`design-token-manage`). Overflow/target-size only (`responsive-breakpoint-verify`).

## Criticality

High: unexplained pixel drift on frozen-motion captures is a gate failure. Tune threshold from fixture evidence (start 0.1).

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`supporting/ui-ux/playwright-visual-testing.md`](../../../../supporting/ui-ux/playwright-visual-testing.md)
- `python scripts/ui-ux/run_visual_regression.py`

## Isolation

`mutate` when writing goldens or results. Parent isolates `scripts` (and `results` if reporting) then spawns `visual-qa-operator`. Parent MUST NOT load this SKILL.md.

## How to use

1. `qmd search --format json --min-score 0.5 -n 5 "visual regression playwright goldens"` then `qmd get` unique files. Do not walk trees.
2. Confirm fixtures under `scripts/ui-ux/fixtures/components/` via the tagged script (not a directory crawl in prose).
3. Compare: `python scripts/ui-ux/run_visual_regression.py --engine synthetic --json`.
4. Optional Chromium: `python scripts/ui-ux/run_visual_regression.py --engine playwright` only when the CI image owns those goldens.
5. Authorized baseline refresh: `python scripts/ui-ux/run_visual_regression.py --update-baselines`.
6. Compress bulky PNG dumps with Headroom (or summarize). Use ast-grep for JSON/YAML frontmatter, not for PNG bytes.

## Dry run

```bash
python scripts/ui-ux/run_visual_regression.py --dry-run --json
python scripts/ai-tooling/validate_skill.py --skill visual-regression-audit --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No secrets. Synthetic fixtures only. Do not ingest product UI from other repos. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Goldens committed only after a green synthetic compare. Report mismatch count and engine. Memory if the capture environment quirk is new.
