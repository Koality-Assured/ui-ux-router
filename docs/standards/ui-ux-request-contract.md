---
doc_kind: requirement
canonical_id: ui-ux-request-contract
purpose: [requirement, reinforcement]
rank: high
topics: [ui-ux, request-contract, accessibility, design-tokens, wcag-2-2]
rag_keywords: [ui-ux-request, contract-normalization, dtcg-tokens, wcag-gate, visual-goldens, responsive-breakpoints]
---

# UI/UX request contract standard

## Scope and relationship to UI/UX standards

This standard governs the intake, normalization, and verification of design token suites, component variant matrices, visual regression goldens, and WCAG accessibility evaluations within `ui-ux-router`.

## Normalized request contract

All operations MUST normalize user instructions into a machine-verifiable record conforming to [`ui-ux-request-v1.schema.json`](./ui-ux-request-v1.schema.json) before generating or evaluating UI components:

```text
Request/version: [id; version; operation: design_token_compile | component_variant_matrix | visual_regression_audit | wcag_accessibility_audit | responsive_breakpoint_verify | micro_interaction_spec]
Design system profile: [system id; token format: dtcg_2025_10 | style_dictionary_v4 | tailwind_v4; color spaces; theme modes]
Target viewports: [array: 375, 768, 1024, 1280, 1440, 1920 CSS pixels]
Intent: [primary objective; user interaction flow; preserve tokens]
Representations: [canonical representations; primary vs supporting; delivery format]
Constraints: [min contrast ratio, touch target bounds, focus indicator styles] (hard | soft)
References: [Figma source specs, design token dictionaries, HTML/CSS component templates]
Accessibility standards: [target level: AA default; min touch target: >= 24px; min contrast: >= 4.5:1 text, >= 3:1 UI; keyboard focusable; reduced motion supported]
Audience & delivery: [recipient role; format: html | css | json | markdown | png_golden]
Provenance: [model tier; timestamp UTC]
Open questions: [breakpoint grid reflow rules, dark-mode token overrides, fallback fonts]
Review & handoff: [owner: authoring operator; reviewer: a11y-compliance-operator; acceptance tests; accessibility gate passed]
```

## Hard and soft constraints in front-end verification

1. **Hard constraints**:
   - WCAG 2.2 AA non-negotiables: Target size minimum of 24×24 CSS px (SC 2.5.8), Focus not obscured (SC 2.4.11), 4.5:1 text contrast (SC 1.4.3), and zero keyboard traps (SC 2.1.2).
   - DTCG format validity: `$value` and `$type` required on all tokens.
   - Any failure of a hard constraint MUST halt the pipeline and reject the PR.

2. **Soft constraints**:
   - Optional AAA enhancements (e.g. 7:1 contrast, 2.4.13 focus appearance).
   - Breakpoint layout preferences that degrade gracefully without text truncation or horizontal overflow.
