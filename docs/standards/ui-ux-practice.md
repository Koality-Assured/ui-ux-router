---
doc_kind: requirement
canonical_id: ui-ux-practice
purpose: [requirement, reinforcement]
rank: high
topics: [ui-ux, accessibility, wcag-2-2, design-tokens, visual-regression]
rag_keywords: [ui-ux-practice, wcag-gate, frozen-motion, dtcg-lint, touch-targets, contrast]
---

# UI/UX engineering practice and accessibility standards

## Scope and authoritative grounding

All component engineering, design token authoring, and front-end auditing within `ui-ux-router` must conform to:
1. **W3C WCAG 2.2 Recommendation (October 2023 / December 2024 update)**: Default target is Level AA.
2. **W3C DTCG Format Module 2025.10**: Authoritative standard for token interchange.
3. **Playwright Visual Comparison Standards**: Governing deterministic headless rendering.

## Non-negotiable practice rules

1. **Mandatory WCAG 2.2 Level AA Non-Regression**:
   - Zero critical or serious accessibility violations allowed on any component deliverable.
   - Touch targets must measure at least 24×24 CSS pixels (SC 2.5.8).
   - Keyboard focus must be visible and unobstructed (SC 2.4.11).
   - Authentication must not block password paste or rely on memorization puzzles (SC 3.3.8).

2. **Deterministic Visual Goldens**:
   - When generating or comparing screenshots, motion MUST be frozen: `* { animation-duration: 0s !important; transition-duration: 0s !important; }`.
   - Fonts must be local and pre-loaded to prevent layout shifts.
   - System clocks must be pinned to prevent timestamp drift.

3. **Strict DTCG Syntax**:
   - All token JSON files must strictly use `$value` and `$type`.
   - Legacy keys (`value`, `type` without `$`) are prohibited and will fail compilation.
