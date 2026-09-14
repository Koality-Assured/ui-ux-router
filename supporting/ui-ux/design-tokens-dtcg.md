---
doc_kind: supporting
canonical_id: design-tokens-dtcg
purpose: [process]
topics: [ui-ux, design-tokens, dtcg]
rag_keywords: [dtcg, style-dictionary, css-variables, tailwind]
---

# DTCG design tokens

Format: Design Tokens Format Module 2025.10 (W3C Community Group Final Report, not a W3C Recommendation). Tokens are JSON objects with `$value`; `$type` on the token or nearest group.

```bash
python scripts/ui-ux/compile_design_tokens.py --dry-run --json
```

Rules in this spoke:

- Reject mixed legacy `value` and DTCG `$value`.
- Fixture subset: `color`, `dimension`, aliases `{group.token}`. Matches Style Dictionary v4 round-trip; full 2025.10 coverage is still incomplete upstream.
- Compile targets: CSS custom properties, SCSS variables, Tailwind `theme.extend` snippet.

Do not import a client Figma file as the token source of truth.
