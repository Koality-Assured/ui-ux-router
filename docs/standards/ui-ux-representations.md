---
doc_kind: requirement
canonical_id: ui-ux-representations
purpose: [requirement, reinforcement]
rank: high
topics: [ui-ux, representations, registry, check-profiles]
rag_keywords: [ui-ux-representations, design-tokens, components, visual-goldens, accessible-dom, micro-interactions]
---

# UI/UX representations standard

## Scope and purpose

This standard defines the normative representation matrix of front-end and design system artifacts recognized by `ui-ux-router`.

Machine-readable mapping is codified in [`ui-ux-representation-registry.json`](./ui-ux-representation-registry.json).

## Representation matrix

### 1. Design tokens (`design_tokens`)
Covers token dictionaries conforming to DTCG Format Module 2025.10 and their platform compiles (CSS custom properties, SCSS, Tailwind).
- **Check profiles**: `dtcg_token_lint`.
- **Key controls**: Strict `$value` and `$type` validation, resolution of `{group.token}` aliases, and prevention of mixing legacy keys.

### 2. Component variant matrices (`component_variant_matrix`)
Covers UI primitives across states (default, hover, focus-visible, active, disabled, loading).
- **Check profiles**: `wcag_22_aa`, `keyboard_focus_path`.
- **Key controls**: 24×24 CSS px minimum touch target (SC 2.5.8), focus not obscured (SC 2.4.11), and focus indicator contrast.

### 3. Visual golden screenshots (`visual_golden_snapshot`)
Covers headless pixel captures across multi-viewport breakpoints (375, 768, 1024, 1280, 1440, 1920px).
- **Check profiles**: `pixel_diff_match`, `reduced_motion`.
- **Key controls**: Freezing animations (`animation-duration: 0s`), local fonts, fixed clocks, and pixel diff threshold enforcement.

### 4. Accessible DOM views (`accessible_dom_view`)
Covers ARIA snapshot trees and axe-core accessibility audit reports.
- **Check profiles**: `wcag_22_aa`, `keyboard_focus_path`.
- **Key controls**: Zero critical/serious axe-core violations, proper landmark roles, valid ARIA attributes, and accessible names.

### 5. Micro-interaction specifications (`micro_interaction_spec`)
Covers CSS and JavaScript transition curves, timing tokens, and gesture choreographies.
- **Check profiles**: `reduced_motion`, `keyboard_focus_path`.
- **Key controls**: Strict adherence to `@media (prefers-reduced-motion: reduce)`, zero flashing content (> 3 flashes/second), and single-pointer operability (SC 2.5.7).

### 6. Theme palettes (`theme_palette`)
Covers multi-theme color systems (light, dark, high contrast).
- **Check profiles**: `wcag_22_aa`, `dtcg_token_lint`.
- **Key controls**: Contrast ratio audits against background tokens (4.5:1 text, 3:1 graphical objects/UI controls).
