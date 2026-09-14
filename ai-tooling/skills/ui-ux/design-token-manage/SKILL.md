---
schema_version: "2.0.0"
name: design-token-manage
description: >-
  Lint and compile W3C DTCG design tokens (JSON $value/$type) to CSS custom properties, SCSS variables, and a Tailwind theme snippet. Use when the user asks for design tokens, Style Dictionary, or DTCG. Do not use for screenshot or axe gates.
owner_agent: design-system-architect
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
  - DTCG JSON path and optional --out-dir for CSS/SCSS/Tailwind artifacts
  outputs:
  - Lint errors (including mixed legacy value keys) or compiled CSS/SCSS/Tailwind snippets
topics: [ui-ux, design-tokens, dtcg]
routing_hints: [tokens, css-variables, style-dictionary]
---

# Design token manage

## When to use

Adding, linting, or compiling design tokens for CSS/SCSS/Tailwind from DTCG JSON.

## When not to use

Visual goldens (`visual-regression-audit`). WCAG scans (`wcag-accessibility-audit`). Importing a client Figma dump as the source of truth.

## Criticality

High: mixed legacy `value` and DTCG `$value` MUST fail. Keep types to the Style Dictionary v4-safe subset until v5 covers Format 2025.10 fully.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`supporting/ui-ux/design-tokens-dtcg.md`](../../../../supporting/ui-ux/design-tokens-dtcg.md)
- `python scripts/ui-ux/compile_design_tokens.py`

## Isolation

`mutate` on token files and compile outputs. Parent isolates `scripts` then spawns `design-system-architect`. Parent MUST NOT load this SKILL.md.

## How to use

1. `qmd search --format json --min-score 0.5 -n 5 "dtcg design tokens style dictionary"` then `qmd get` unique files. Do not walk trees.
2. Lint/compile: `python scripts/ui-ux/compile_design_tokens.py --json`.
3. Write artifacts: `python scripts/ui-ux/compile_design_tokens.py --out-dir <dir>`.
4. Inspect token JSON structure with ast-grep (`-k pair`); compress bulky compile dumps with Headroom.

## Dry run

```bash
python scripts/ui-ux/compile_design_tokens.py --dry-run --json
python scripts/ai-tooling/validate_skill.py --skill design-token-manage --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No secrets. Synthetic fixtures only. Do not ingest product UI from other repos. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Zero lint errors on the fixture dictionary. Compiled snippets written only when `--out-dir` is authorized.
