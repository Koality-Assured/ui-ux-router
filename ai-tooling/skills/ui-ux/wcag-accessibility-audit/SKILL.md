---
schema_version: "2.0.0"
name: wcag-accessibility-audit
description: >-
  Run automated WCAG 2.2 AA checks (contrast, keyboard trap, landmarks, unlabeled controls, target size) on synthetic fixtures, with optional axe-core tags. Use when the user asks for accessibility audit, axe, or WCAG 2.2. Do not use for screenshot goldens (visual-regression-audit).
owner_agent: a11y-compliance-operator
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
  - HTML fixture paths, fail-on finding ids, and optional axe engine
  outputs:
  - Impact-grouped findings and a non-zero exit when planted contrast, trap, unlabeled, or target-size cases remain gated
topics: [ui-ux, accessibility, wcag, axe-core]
routing_hints: [axe, contrast, keyboard-trap]
---

# Wcag accessibility audit

## When to use

Automated accessibility gates, axe-core tag runs, keyboard-trap checks, or contrast failures on synthetic components.

## When not to use

Pixel goldens (`visual-regression-audit`). Token compile (`design-token-manage`). Claiming WCAG certification from axe.

## Criticality

High: planted contrast and keyboard-trap fixtures MUST fail the gate. Axe cannot prove conformance.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`supporting/ui-ux/axe-core-a11y-auditing.md`](../../../../supporting/ui-ux/axe-core-a11y-auditing.md)
- `python scripts/ui-ux/audit_accessibility.py`

## Isolation

`mutate` when writing results. Parent isolates then spawns `a11y-compliance-operator`. Parent MUST NOT load this SKILL.md.

## How to use

1. `qmd search --format json --min-score 0.5 -n 5 "wcag 2.2 axe keyboard trap"` then `qmd get` unique files. Do not walk trees.
2. Run `python scripts/ui-ux/audit_accessibility.py --engine synthetic --json`.
3. Optional: `--engine axe` when Node/`npx` can run `@axe-core/cli` with tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22a,wcag22aa.
4. Confirm planted `button-fail-contrast.html` and `modal-fail-trap.html` appear in findings.
5. Compress bulky axe JSON with Headroom. Use ast-grep for structured HTML/JSON facts.

## Dry run

```bash
python scripts/ui-ux/audit_accessibility.py --dry-run --json
python scripts/ai-tooling/validate_skill.py --skill wcag-accessibility-audit --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No secrets. Synthetic fixtures only. Do not ingest product UI from other repos. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Gated findings listed. Do not claim certification. Write residual manual checks to the overlay or supporting recipe if new.
