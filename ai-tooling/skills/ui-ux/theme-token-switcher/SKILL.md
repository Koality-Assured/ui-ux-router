---
schema_version: "2.0.0"
name: theme-token-switcher
description: >-
  Architect, compile, and validate multi-theme design token switching, semantic CSS variable scoping, and theme persistence contracts. Use when implementing theme switching, authoring dark mode or high-contrast token overrides, or validating theme contrast ratios. Do not use for single-theme DTCG token compilation (design-token-manage).
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
  - Base semantic design token dictionary and theme override sets (dark, high-contrast, brand palettes)
  - Theme scoping strategy ([data-theme] attribute, media queries, CSS custom properties) and persistence target (localStorage, cookies)
  outputs:
  - Compiled multi-theme CSS stylesheet with scoped custom properties
  - Anti-flash (FOUT) inline script pattern and contrast verification report across all theme permutations
topics: [ui-ux, design-tokens, theme-switcher, dark-mode, high-contrast, css-variables]
tags: [ui-ux, design-tokens, theme-switcher, dark-mode, high-contrast, css-variables]
routing_hints: [theme, dark-mode, color-scheme, theme-switcher, multi-theme, high-contrast]
---

# Theme token switcher

## When to use

Architecting and compiling multi-theme token structures (light, dark, high contrast, brand variants), implementing semantic CSS custom property switching via `[data-theme="..."]` or `@media (prefers-color-scheme)`, ensuring Windows High Contrast mode compatibility (`@media (forced-colors: active)`), and preventing Flash of Unstyled Theme (FOUT/FOIT).

## When not to use

Single-theme base token compilation or DTCG schema linting (`design-token-manage`). Screenshot diffing across themes (`visual-regression-audit`).

## Criticality

High: hardcoded color values and mismatched contrast ratios between themes introduce severe accessibility violations in dark and high-contrast modes. Semantic tokens MUST guarantee minimum WCAG 2.2 AA contrast (4.5:1 for body text, 3:1 for graphical objects and large text) across EVERY active theme.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/design-token-manage/SKILL.md`](../design-token-manage/SKILL.md)
- W3C CSS Color Module Level 4 & CSS Custom Properties for Cascading Variables Module Level 1

## Isolation

`mutate` when writing or editing multi-theme token files, compiled CSS custom properties, or theme-switching scripts. Parent isolates via `spawn_worktree.py` before spawning `design-system-architect`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing design tokens and theme structures:
   `qmd search --format json --min-score 0.5 -n 5 "theme token switcher dark mode high contrast css variables"` then `qmd get` matching files.
2. Structure the three-tier token hierarchy:
   - **Tier 1 (Global / Primitives):** Immutable raw values (`blue-500: #3b82f6`, `gray-900: #111827`, `white: #ffffff`).
   - **Tier 2 (Semantic / Contextual):** Purpose-driven tokens that change values per theme (`--color-surface-base`, `--color-surface-card`, `--color-text-primary`, `--color-border-subtle`, `--color-action-primary`).
   - **Tier 3 (Component):** Component-specific bindings referencing semantic tokens (`--button-primary-bg: var(--color-action-primary)`).
   - Only Tier 2 Semantic tokens are redefined across themes!
3. Compile theme scopes into scoped CSS custom properties:
   ```css
   /* Default / Light theme */
   :root, [data-theme="light"] {
     --color-surface-base: #f8fafc;
     --color-surface-card: #ffffff;
     --color-text-primary: #0f172a;
     --color-text-muted: #64748b;
     --color-border-subtle: #e2e8f0;
     --color-action-primary: #2563eb;
     --color-focus-ring: #3b82f6;
     color-scheme: light;
   }

   /* Dark theme override */
   [data-theme="dark"] {
     --color-surface-base: #0f172a;
     --color-surface-card: #1e293b;
     --color-text-primary: #f8fafc;
     --color-text-muted: #94a3b8;
     --color-border-subtle: #334155;
     --color-action-primary: #3b82f6;
     --color-focus-ring: #60a5fa;
     color-scheme: dark;
   }

   /* High-Contrast / Accessible theme override */
   [data-theme="high-contrast"] {
     --color-surface-base: #000000;
     --color-surface-card: #000000;
     --color-text-primary: #ffffff;
     --color-text-muted: #ffff00;
     --color-border-subtle: #ffffff;
     --color-action-primary: #00ffff;
     --color-focus-ring: #ffff00;
     color-scheme: dark;
   }
   ```
4. Support Windows High Contrast / Forced Colors:
   ```css
   @media (forced-colors: active) {
     :root {
       --color-surface-base: Canvas;
       --color-surface-card: Canvas;
       --color-text-primary: CanvasText;
       --color-border-subtle: ButtonBorder;
       --color-action-primary: Highlight;
       --color-focus-ring: Highlight;
     }
   }
   ```
5. Prevent Flash of Inaccurate Theme (FOUT):
   - Place a lightweight synchronous inline script in `<head>` before any stylesheet or body rendering:
     ```html
     <script>
       (function() {
         const stored = localStorage.getItem('theme-preference');
         const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
         const theme = stored || (systemDark ? 'dark' : 'light');
         document.documentElement.setAttribute('data-theme', theme);
       })();
     </script>
     ```
6. Audit color contrast across all themes:
   - Calculate relative luminance and ensure contrast ratio $C = \frac{L_1 + 0.05}{L_2 + 0.05} \ge 4.5:1$ between `--color-text-primary` and `--color-surface-base` in every theme.
7. Inspect token mappings using ast-grep; compress multi-theme CSS output with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill theme-token-switcher --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic themes only. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Multi-theme stylesheet compiled with verified custom property scoping. Minimum 4.5:1 contrast verified across light, dark, and high-contrast themes. Anti-flash inline script and forced-colors fallback included.
