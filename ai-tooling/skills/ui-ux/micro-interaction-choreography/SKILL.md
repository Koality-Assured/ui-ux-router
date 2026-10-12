---
schema_version: "2.0.0"
name: micro-interaction-choreography
description: >-
  Specify, choreograph, and validate UI micro-interactions, transition curves, spring physics, entrance and exit choreography, and prefers-reduced-motion fallbacks. Use when choreographing micro-interactions, defining animation timings, easing curves, or implementing reduced-motion contracts. Do not use for static breakpoint verification (responsive-breakpoint-verify) or token linting (design-token-manage).
owner_agent: interaction-designer
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
  - Interaction event trigger (hover, tap, expand, dismiss, route-change) and target UI component
  - Motion parameters (property, duration, easing, stagger index, motion preference mode)
  outputs:
  - Motion choreography specification sheet with cubic-bezier curves, keyframes, and timing tokens
  - Strict prefers-reduced-motion fallback rules and deterministic test stabilization switches
topics: [ui-ux, micro-interactions, animation, easing, choreography, reduced-motion]
tags: [ui-ux, micro-interactions, animation, easing, choreography, reduced-motion]
routing_hints: [motion, animation, easing, transitions, micro-interactions, spring]
---

# Micro-interaction choreography

## When to use

Authoring motion choreography specifications for UI micro-interactions (button feedback, accordion expand/collapse, modal presentation, drawer slide-overs, tab switching, toast banners, skeleton pulses), tuning cubic-bezier curves and spring physics, establishing staggered entrance sequences, and writing robust `@media (prefers-reduced-motion: reduce)` accessible fallbacks.

## When not to use

Static breakpoint layout verification (`responsive-breakpoint-verify`). Comparing raster pixel goldens under frozen motion (`visual-regression-audit`). Compiling static color/typography tokens (`design-token-manage`).

## Criticality

High: excessive, non-choreographed, or abrupt motion causes disorientation, cognitive overload, and vestibular motion sickness (WCAG 2.3.3). Motion MUST be meaningful, spatial, performant (composite-only properties `transform` and `opacity`), and fully respect system reduced-motion settings.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/responsive-breakpoint-verify/SKILL.md`](../responsive-breakpoint-verify/SKILL.md)
- W3C CSS Transitions and Animations Level 2 Specifications

## Isolation

`mutate` when generating or modifying motion specifications, CSS transition tokens, or animation testbeds. Parent isolates via `spawn_worktree.py` before spawning `interaction-designer`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing interaction and responsive rules:
   `qmd search --format json --min-score 0.5 -n 5 "micro-interaction animation easing choreography reduced-motion"` then `qmd get` matching files.
2. Select standardized duration tiers according to interaction scale:
   - **Micro (100ms - 150ms):** Instant tactile feedback: button press downscale (`scale(0.97)`), toggle switch flip, checkbox checkmark drawing.
   - **Standard / State (200ms - 300ms):** Contextual component state transitions: dropdown opening, tooltip fade, accordion expansion, tab underline slide.
   - **Macro / Structural (350ms - 500ms):** Major viewport changes: modal backdrop fade and dialog scale-in, slide-over drawer entrance, page view transitions.
   - Never exceed 500ms for user-initiated UI micro-interactions.
3. Apply standard cubic-bezier easing tokens based on physics intent:
   - **Standard / Smooth (`cubic-bezier(0.4, 0.0, 0.2, 1)`):** On-screen elements shifting position or resizing.
   - **Decelerate / Entrance (`cubic-bezier(0.0, 0.0, 0.2, 1)`):** Elements entering the viewport from off-screen or fading into view.
   - **Accelerate / Exit (`cubic-bezier(0.4, 0.0, 1, 1)`):** Elements exiting the viewport or closing.
   - **Snappy Spring (`cubic-bezier(0.34, 1.56, 0.64, 1)`):** Expressive interactive badges, success icons, or bottom-sheet snap points.
4. Choreograph staggered entrances:
   - For lists, grids, or multi-element reveals, stagger child item animations by 30ms - 50ms per item with a maximum ceiling of 300ms total stagger time:
     ```css
     .stagger-item:nth-child(1) { animation-delay: 0ms; }
     .stagger-item:nth-child(2) { animation-delay: 40ms; }
     .stagger-item:nth-child(3) { animation-delay: 80ms; }
     ```
5. Enforce strict `prefers-reduced-motion` compliance:
   - When reduced motion is preferred, replace spatial displacement (sliding, scaling, rotating) with instantaneous cuts or gentle crossfades:
     ```css
     @media (prefers-reduced-motion: reduce) {
       *, ::before, ::after {
         animation-duration: 0.01ms !important;
         animation-iteration-count: 1 !important;
         transition-duration: 0.01ms !important;
         scroll-behavior: auto !important;
       }
     }
     ```
6. Implement deterministic QA freeze mode:
   - Define `--motion-duration-factor: 1` as a global token that can be toggled to `0` during visual regression tests (`visual-regression-audit`) to prevent flakiness and screenshot race conditions.
7. Inspect motion CSS and keyframes using ast-grep; compress lengthy animation timelines with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill micro-interaction-choreography --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic interaction patterns only. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Complete motion specification with duration, easing, property targets, and stagger sequences documented. Comprehensive `prefers-reduced-motion` fallbacks verified. Zero layout-thrashing properties used (limit strictly to `transform` and `opacity`).
