---
schema_version: "2.0.0"
name: component-variant-matrix
description: >-
  Define, generate, and validate multi-dimensional component variant matrices covering visual states, size scales, and intent permutations. Use when defining component variant matrices, generating story or fixture permutations, or auditing interactive state completeness. Do not use for automated axe scans (wcag-accessibility-audit) or pixel golden diffing (visual-regression-audit).
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
  - Component specification or prop contract with variant dimensions (size, intent, appearance) and interactive states
  - Target output schema or fixture format (HTML fixture, JSON variant catalog, or TypeScript/CVA definitions)
  outputs:
  - Multi-dimensional component variant matrix schema and permutation catalog
  - State completeness report identifying missing interactive or disabled representations
topics: [ui-ux, design-systems, component-matrix, cva, variant-permutations]
tags: [ui-ux, design-systems, component-matrix, cva, variant-permutations]
routing_hints: [variants, component-states, matrix, props, permutations]
---

# Component variant matrix

## When to use

Defining exhaustive component variant specifications, calculating combinatorial prop matrices (size, intent, appearance, shape), authoring Class Variance Authority (CVA) or CSS module contracts, and generating synthetic HTML testbed fixtures for visual regression testing.

## When not to use

Automated WCAG contrast or landmark audits (`wcag-accessibility-audit`). Multi-breakpoint responsive layout overflow tests (`responsive-breakpoint-verify`). Comparing raster pixel goldens against baseline PNGs (`visual-regression-audit`).

## Criticality

High: missing states (unhandled `disabled`, absent `focus-visible`, untyped `loading`, or unconstrained compound variants) cause visual regressions and runtime styling collisions. All interactive components MUST define explicit base, hover, active, focus-visible, and disabled styles.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/design-token-manage/SKILL.md`](../design-token-manage/SKILL.md)
- Component fixture directory: `scripts/ui-ux/fixtures/components/`

## Isolation

`mutate` on component specs, variant matrices, and fixture templates. Parent isolates via `spawn_worktree.py` before spawning `design-system-architect`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing component definitions and tokens via qmd:
   `qmd search --format json --min-score 0.5 -n 5 "component variant matrix states props"` then `qmd get` matching files.
2. Identify orthogonal variant dimensions versus dynamic interactive states:
   - **Dimensions:** Size (`sm`, `md`, `lg`), Intent (`primary`, `secondary`, `destructive`, `ghost`, `outline`), Elevation/Surface (`flat`, `raised`, `overlay`).
   - **Interactive States:** `default`, `hover`, `active`, `focus-visible`, `disabled`, `loading`.
3. Compute the combinatorial matrix ($S \times I \times E$) while pruning invalid compound permutations through explicit compound variant rules:
   ```typescript
   // Example CVA mapping
   const buttonVariants = cva(
     "base-button font-medium rounded-md transition-colors focus-visible:outline-2",
     {
       variants: {
         intent: {
           primary: "bg-primary text-primary-fg hover:bg-primary-hover",
           secondary: "bg-secondary text-secondary-fg hover:bg-secondary-hover",
           destructive: "bg-destructive text-destructive-fg hover:bg-destructive-hover",
           ghost: "hover:bg-muted text-muted-fg",
         },
         size: {
           sm: "h-8 px-3 text-xs gap-1.5",
           md: "h-10 px-4 text-sm gap-2",
           lg: "h-12 px-6 text-base gap-2.5",
         },
       },
       defaultVariants: {
         intent: "primary",
         size: "md",
       },
     }
   );
   ```
4. Emit static HTML fixture matrices under `scripts/ui-ux/fixtures/components/` displaying all state permutations side-by-side on neutral backgrounds.
5. Verify state completeness:
   - Ensure every interactive variant includes `:disabled` / `aria-disabled="true"` with pointer-events disabled or neutralized cursor.
   - Ensure `:focus-visible` defines an unmistakable ring complying with WCAG 2.4.7.
   - Ensure `loading` states include `aria-busy="true"` and accessible replacement text.
6. Inspect generated fixtures with ast-grep (`-k pair` or `-k element`); compress bulky matrix JSON or HTML fixture dumps with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill component-variant-matrix --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic fixtures only. Do not ingest product UI from external repositories. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Complete variant schema generated. Zero unmapped interactive states across the declared dimension matrix. Synthetic HTML testbed fixtures verified for visual QA handoff.
