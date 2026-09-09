---
doc_kind: requirement
canonical_id: ui-ux-overlay
purpose: [requirement]
rank: medium
topics: [ui-ux, overlay]
rag_keywords: [ui-ux, domain-overlay, spoke]
---

# ui ux domain overlay

This spoke is a `ui-ux` harness scaffolded from `ai-harness-core`. Feed ui ux corpus here. Keep generic machinery in the core.

Do not copy this overlay, instance `projects/`, `research/`, or `ai-tooling/memory/` back to the generic core.

Pull core updates: `python scripts/sync/pull_harness_core.py --dry-run --json`.

Propose generic core changes: `python scripts/sync/propose_core_update.py --dry-run --json`.
