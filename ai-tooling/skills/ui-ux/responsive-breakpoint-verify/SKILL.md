---
schema_version: "2.0.0"
name: responsive-breakpoint-verify
description: >-
  Verify multi-viewport layout integrity on synthetic fixtures (mobile, tablet, desktop, ultra-wide): no horizontal overflow, no clipped text, grid reflow, and 24x24 CSS-pixel minimum targets. Use when the user asks for breakpoint, responsive, or touch-target checks. Do not use as a substitute for pixel goldens (visual-regression-audit).
owner_agent: interaction-designer
rank: high
isolation: read-only
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
  - Fixture set and viewport list (default 375/768/1280/1920)
  outputs:
  - Layout-integrity findings for overflow and sub-minimum touch targets per viewport
topics: [ui-ux, responsive, breakpoints]
routing_hints: [viewport, overflow, touch-target]
---

# Responsive breakpoint verify

## When to use

Checking reflow, overflow, or WCAG 2.5.8 target size across breakpoints.

## When not to use

Pixel-perfect golden compare (`visual-regression-audit`). Contrast/keyboard-trap (`wcag-accessibility-audit`).

## Criticality

High: 24 CSS-pixel minimum is WCAG 2.2 AA (2.5.8). Comfortable 48x48 is a fixture rule when declared.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- `python scripts/ui-ux/run_visual_regression.py --check-layout`

## Isolation

`read-only` compare. Parent isolates if results will be written, then spawns `interaction-designer`. Parent MUST NOT load this SKILL.md.

## How to use

1. `qmd search --format json --min-score 0.5 -n 5 "responsive breakpoint touch target overflow"` then `qmd get` unique files. Do not walk trees.
2. `python scripts/ui-ux/run_visual_regression.py --check-layout --json`.
3. Treat `button-fail-target.html` as a planted 2.5.8 failure.
4. Use ast-grep for HTML/JSON structure; compress bulky JSON with Headroom.

## Dry run

```bash
python scripts/ui-ux/run_visual_regression.py --check-layout --dry-run --json
python scripts/ai-tooling/validate_skill.py --skill responsive-breakpoint-verify --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No secrets. Synthetic fixtures only. Do not ingest product UI from other repos. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Layout findings listed per viewport. Bind screenshot mismatches to `visual-regression-audit` rather than duplicating goldens here.
