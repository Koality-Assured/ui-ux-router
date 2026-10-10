# Skills

Human overview: router skills live organized into domain families under `<family>/<name>/SKILL.md`.

**Agents do not use this README as a catalog.** They load [`../../routing/skill-dispatch.md`](../../routing/skill-dispatch.md) (regenerate with `python scripts/routing/generate_skill_dispatch.py`) and spawn `owner_agent`. Template: [`../../ai-tooling/skills/skill-conventions.md`](skill-conventions.md). Validate: `python scripts/ai-tooling/validate_skill.py --all`.

Human index (not agent SoT):

| Skill | Owner | Isolation |
| --- | --- | --- |
| [`agent-builder/`](./meta/agent-builder/) | harness-operator | mutate |
| [`agent-cost-estimator/`](./benchmarks/agent-cost-estimator/) | benchmark-agent | mutate |
| [`agent-fleet-benchmark/`](./benchmarks/agent-fleet-benchmark/) | benchmark-agent | mutate |
| [`antagonistic-review/`](./meta/antagonistic-review/) | detailed-activity | read-only |
| [`anti-slop/`](./reporting/anti-slop/) | document-operator | mutate |
| [`architecture-diagram/`](./reporting/architecture-diagram/) | document-operator | mutate |
| [`ast-grep/`](./cost-layers/ast-grep/) | harness-operator | read-only |
| [`code-review-report/`](./reporting/code-review-report/) | artifact-agent | mutate |
| [`component-variant-matrix/`](./ui-ux/component-variant-matrix/) | design-system-architect | mutate |
| [`corpus-draft/`](./reporting/corpus-draft/) | document-operator | mutate |
| [`cost-layer-dry-run/`](./cost-layers/cost-layer-dry-run/) | harness-operator | mutate |
| [`deep-research/`](./meta/deep-research/) | research-operator | mutate |
| [`design-token-manage/`](./ui-ux/design-token-manage/) | design-system-architect | mutate |
| [`doc-builder/`](./meta/doc-builder/) | document-operator | mutate |
| [`executive-report/`](./reporting/executive-report/) | document-operator | mutate |
| [`focus-keyboard-navigation/`](./ui-ux/focus-keyboard-navigation/) | a11y-compliance-operator | mutate |
| [`git-basics/`](./git/git-basics/) | git-fast-operator | mutate |
| [`github-paths/`](./git/github-paths/) | github-ops | read-only |
| [`github-workflow/`](./git/github-workflow/) | github-ops | mutate |
| [`guidance-draft/`](./reporting/guidance-draft/) | document-operator | mutate |
| [`harness-review/`](./harness-review/) | harness-operator | mutate |
| [`headroom/`](./cost-layers/headroom/) | harness-operator | read-only |
| [`humanizer/`](./reporting/humanizer/) | document-operator | mutate |
| [`information-architecture-map/`](./ui-ux/information-architecture-map/) | interaction-designer | mutate |
| [`isolate-work/`](./meta/isolate-work/) | router | mutate |
| [`local-webfetch/`](./research/local-webfetch/) | research-operator | read-only |
| [`markdownlint/`](./meta/markdownlint/) | document-operator | mutate |
| [`memory-adjust/`](./memory/memory-adjust/) | harness-operator | mutate |
| [`memory-cleanup/`](./memory/memory-cleanup/) | harness-operator | mutate |
| [`memory-create/`](./memory/memory-create/) | harness-operator | mutate |
| [`mermaid-diagram/`](./reporting/mermaid-diagram/) | document-operator | mutate |
| [`micro-interaction-choreography/`](./ui-ux/micro-interaction-choreography/) | interaction-designer | mutate |
| [`model-memory-operate/`](./model-memory-operate/) | harness-operator | mutate |
| [`navigation-flow-spec/`](./ui-ux/navigation-flow-spec/) | interaction-designer | mutate |
| [`proposal-report/`](./reporting/proposal-report/) | document-operator | mutate |
| [`qmd-efficiency/`](./meta/qmd-efficiency/) | harness-operator | mutate |
| [`qmd-usage/`](./meta/qmd-usage/) | harness-operator | read-only |
| [`readme-maintain/`](./meta/readme-maintain/) | document-operator | mutate |
| [`reference-maintain/`](./meta/reference-maintain/) | document-operator | mutate |
| [`responsive-breakpoint-verify/`](./ui-ux/responsive-breakpoint-verify/) | interaction-designer | read-only |
| [`retrieval-benchmark/`](./benchmarks/retrieval-benchmark/) | benchmark-agent | mutate |
| [`router-structure/`](./meta/router-structure/) | document-operator | read-only |
| [`scratch-cleanup/`](./meta/scratch-cleanup/) | harness-operator | mutate |
| [`screen-reader-semantics/`](./ui-ux/screen-reader-semantics/) | a11y-compliance-operator | mutate |
| [`script-builder/`](./meta/script-builder/) | harness-operator | mutate |
| [`skill-builder/`](./meta/skill-builder/) | harness-operator | mutate |
| [`skill-dry-run/`](./meta/skill-dry-run/) | harness-operator | read-only |
| [`task-eval-benchmark/`](./benchmarks/task-eval-benchmark/) | benchmark-agent | mutate |
| [`theme-token-switcher/`](./ui-ux/theme-token-switcher/) | design-system-architect | mutate |
| [`tool-efficiency-benchmark/`](./benchmarks/tool-efficiency-benchmark/) | benchmark-agent | mutate |
| [`typography-scale-calc/`](./ui-ux/typography-scale-calc/) | design-system-architect | mutate |
| [`visual-regression-audit/`](./ui-ux/visual-regression-audit/) | visual-qa-operator | mutate |
| [`wcag-accessibility-audit/`](./ui-ux/wcag-accessibility-audit/) | a11y-compliance-operator | mutate |
