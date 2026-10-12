---
schema_version: "2.0.0"
name: typography-scale-calc
description: >-
  Calculate, generate, and validate modular typography scales, fluid clamp() formulas, line-height ratios, and letter-spacing tracking tokens across viewport ranges. Use when defining typographic scales, calculating fluid typography clamp() values, or generating type tokens for design systems. Do not use for multi-breakpoint layout overflow checks (responsive-breakpoint-verify).
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
  - Base font size (in px or rem), scale ratio (e.g. Major Third 1.25, Perfect Fourth 1.333), viewport bounds, and line-height ratio rules
  - Target format (DTCG JSON tokens, CSS custom properties, or SCSS mixins)
  outputs:
  - Modular type scale table, fluid clamp() formulas, and paired line-height / letter-spacing token definitions
  - Synthesized CSS custom property declarations and DTCG typography token definitions
topics: [ui-ux, typography, type-scale, fluid-typography, clamp, design-tokens]
tags: [ui-ux, typography, type-scale, fluid-typography, clamp, design-tokens]
routing_hints: [typography, font-scale, clamp, line-height, modular-scale]
---

# Typography scale calc

## When to use

Designing mathematical modular type scales, calculating fluid typography using CSS `clamp()` across min/max viewport bounds, defining proportional line heights (leading) and letter-spacing (tracking) tokens, and compiling typographic variables into DTCG design tokens or CSS custom properties.

## When not to use

Checking viewport overflow or touch targets (`responsive-breakpoint-verify`). Auditing contrast or font legibility under WCAG (`wcag-accessibility-audit`). Multi-breakpoint screenshot regressions (`visual-regression-audit`).

## Criticality

High: arbitrary font sizes and hardcoded pixel values create visual dissonance, unmaintainable stylesheets, and layout shifts. Fluid clamp typography must prevent text truncation at narrow viewports (320px) while maintaining legibility and vertical rhythm at ultra-wide viewports (1920px).

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/design-token-manage/SKILL.md`](../design-token-manage/SKILL.md)
- W3C DTCG Typography Token Specification

## Isolation

`mutate` when generating or updating typography tokens and CSS variables. Parent isolates via `spawn_worktree.py` before spawning `design-system-architect`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing design tokens:
   `qmd search --format json --min-score 0.5 -n 5 "typography scale tokens clamp line-height"` then `qmd get` matching files.
2. Select an appropriate modular scale ratio based on application archetype:
   - **Minor Third (1.200):** High-density dashboards, technical consoles, compact data tables.
   - **Major Third (1.250):** Standard web applications, SaaS dashboards, balanced body/heading hierarchy.
   - **Perfect Fourth (1.333):** Content-rich blogs, documentation sites, editorial layouts.
   - **Golden Ratio (1.618):** Expressive marketing sites, landing pages, high-contrast hero displays.
3. Compute scale step values from base font size $S_0$ (default 16px / 1rem):
   $$S_n = S_0 \times r^n \quad (n \in \{-2, -1, 0, 1, 2, 3, 4, 5, 6\})$$
   - `xs`: $n = -2$ (~11.1px)
   - `sm`: $n = -1$ (~12.8px)
   - `base`: $n = 0$ (16.0px)
   - `lg`: $n = 1$ (20.0px for 1.25)
   - `xl`: $n = 2$ (25.0px)
   - `2xl`: $n = 3$ (31.25px)
   - `3xl`: $n = 4$ (39.06px)
   - `4xl`: $n = 5$ (48.83px)
4. Compute responsive fluid typography using linear interpolation between minimum viewport $W_{min}$ (e.g. 375px) and maximum viewport $W_{max}$ (e.g. 1280px):
   $$\text{slope} = \frac{S_{max} - S_{min}}{W_{max} - W_{min}}$$
   $$\text{intercept} = S_{min} - \text{slope} \times W_{min}$$
   $$\text{fluid} = \text{clamp}(S_{min}\text{rem}, (\text{slope} \times 100)\text{vw} + \text{intercept}\text{rem}, S_{max}\text{rem})$$
5. Pair line-height and letter-spacing (tracking) tokens inversely to font size:
   - Display headings (`3xl`, `4xl`): tight leading (`1.1` - `1.2`), tight tracking (`-0.02em` to `-0.01em`).
   - Section headings (`lg`, `xl`, `2xl`): moderate leading (`1.25` - `1.35`), neutral tracking (`0em`).
   - Body copy (`base`, `sm`): comfortable leading (`1.5` - `1.65`), neutral tracking (`0em`).
   - Micro text / uppercase captions (`xs`): loose leading (`1.4`), wide tracking (`+0.05em`).
6. Export tokens to DTCG format and CSS custom properties:
   ```css
   :root {
     --font-size-base: 1rem;
     --font-size-3xl: clamp(1.875rem, 1.34rem + 2.28vw, 2.441rem);
     --line-height-3xl: 1.15;
     --letter-spacing-3xl: -0.015em;
   }
   ```
7. Use ast-grep to inspect compiled CSS/JSON structures; compress large scale matrices with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill typography-scale-calc --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Mathematical and token formulas only. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Complete modular type scale generated with paired line-height and letter-spacing values. All fluid clamp() calculations mathematically verified within bounded viewports. Token artifacts validated against DTCG schema.
