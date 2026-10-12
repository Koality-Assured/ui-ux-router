# Scripts

> [!IMPORTANT]
> **Human-Facing Documentation Only**: This README is maintained strictly for human developers and repository visitors. Autonomous AI agents MUST NOT ingest or utilize `README.md` files for operational instructions or context. All agent directives and navigation reside strictly in [`AGENTS.md`](../AGENTS.md) and [`routing/`](../routing/).

Tagged Python utilities in purpose subfolders. Index: [`script-index.md`](./script-index.md) (generated). Shared helpers live in [`_lib/`](./_lib/) and are not indexed.

| Subfolder | Role |
| --- | --- |
| [`_lib/`](./_lib/) | Shared helpers (`md.py`, `paths.py`) — not indexed |
| [`change-history/`](./change-history/) | Provenance append / quarter files |
| [`routing/`](./routing/) | Script index, skill dispatch, worktree spawn |
| [`qmd/`](./qmd/) | Collections, index refresh, retrieval dry-run |
| [`cost-layers/`](./cost-layers/) | Combined qmd + Headroom validation |
| [`ai-tooling/`](./ai-tooling/) | Skill catalog validator |
| [`docs/`](./docs/) | Wiki structure validator |
| [`ui-ux/`](./ui-ux/) | Design token compilation, accessibility audits, visual regression |

Invoke as `python scripts/<purpose>/<name>.py`. Regenerate the index after add/remove/rename: `python scripts/routing/generate_script_index.py`.
