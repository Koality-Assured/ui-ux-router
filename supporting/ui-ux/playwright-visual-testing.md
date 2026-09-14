---
doc_kind: supporting
canonical_id: playwright-visual-testing
purpose: [process]
topics: [ui-ux, playwright, visual-regression]
rag_keywords: [playwright, toHaveScreenshot, goldens, pixelmatch, reduced-motion]
---

# Playwright visual testing

Recipe for screenshot gates in this spoke. Official API: Playwright visual comparisons (`toHaveScreenshot`). Default harness gate is `python scripts/ui-ux/run_visual_regression.py --engine synthetic` so goldens stay OS-stable.

## Stabilize captures

- Freeze motion: `animation-duration: 0s` and `transition-duration: 0s` on `*` (fixtures already do this). Playwright: `animations="disabled"` and `emulate_media(reduced_motion="reduce")`.
- Fonts: local `@font-face` with `font-display: block` so glyph swap does not shift layout.
- Clocks: `page.clock.setFixedTime()` when a fixture shows timestamps.
- Pixelmatch threshold starts at `0.1`; tune from fixture evidence.

## Engines

| Engine | When |
| --- | --- |
| `synthetic` | Default CI. Deterministic PNG raster of `data-*` boxes. |
| `playwright` | Same OS + Chromium image that owns those goldens. `--update-baselines` on that image only. |

Viewports: 375 / 768 / 1280 / 1920 CSS pixels. Synthetic goldens use height 80 (stable strip), full width.

Do not treat a cross-OS Playwright miss as a product bug until environments match.
