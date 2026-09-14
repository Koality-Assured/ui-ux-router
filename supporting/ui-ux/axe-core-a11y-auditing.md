---
doc_kind: supporting
canonical_id: axe-core-a11y-auditing
purpose: [process]
topics: [ui-ux, accessibility, wcag, axe-core]
rag_keywords: [axe-core, wcag22aa, contrast, keyboard-trap, landmarks]
---

# axe-core accessibility auditing

Automated WCAG 2.2 AA subset for synthetic fixtures. Official tags include `wcag22a` / `wcag22aa` (Playwright samples often omit 2.2). Axe cannot prove conformance.

## Default gate

```bash
python scripts/ui-ux/audit_accessibility.py --engine synthetic --json
```

Planted failures that MUST appear:

- `button-fail-contrast.html` — relative-luminance contrast below 4.5:1
- `modal-fail-trap.html` — Tab `preventDefault` / `data-keyboard-trap`
- `form-fail-unlabeled.html` — control without label or `aria-label`
- `button-fail-target.html` — target below 24 CSS pixels (SC 2.5.8)

## Optional axe-core

`--engine axe` runs `npx @axe-core/cli` with tags `wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22a,wcag22aa` when Node is on PATH. Treat stdout as advisory; compress bulky JSON (Headroom).

APCA contrast is not a v1 gate; relative luminance is.
