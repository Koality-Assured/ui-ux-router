---
schema_version: "2.0.0"
name: information-architecture-map
description: >-
  Structure, document, and validate application information architecture (IA), hierarchical sitemaps, content taxonomy, navigation depth levels, and semantic URL schemas. Use when mapping application sitemaps, organizing content hierarchies, evaluating navigation depth, or designing taxonomy structures. Do not use for step-by-step user journey transition specs (navigation-flow-spec).
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
  - Content inventory, domain entity model, functional zones, and business workflow requirements
  - Target navigation hierarchy constraints (maximum click depth, primary navigation capacity)
  outputs:
  - Information architecture map with hierarchical visual tree (Mermaid diagram), taxonomy schema, and URL routing blueprints
  - Navigation depth scorecard and wayfinding consistency audit across application zones
topics: [ui-ux, information-architecture, sitemap, taxonomy, navigation-depth, content-hierarchy]
tags: [ui-ux, information-architecture, sitemap, taxonomy, navigation-depth, content-hierarchy]
routing_hints: [ia, sitemap, hierarchy, taxonomy, navigation-depth, wayfinding]
---

# Information architecture map

## When to use

Constructing comprehensive information architecture maps, designing hierarchical sitemaps, establishing content taxonomy and classification structures, analyzing navigation click depth (ensuring critical tasks are reachable in $\le 3$ clicks), designing wayfinding schemas (breadcrumbs, sidebars, tabs, global navigation), and defining semantic URL routing structures.

## When not to use

Specifying microscopic view transitions, modal stack lifecycles, or state machine triggers (`navigation-flow-spec`). Authoring UI copy or editorial prose (`guidance-draft`).

## Criticality

High: poor information architecture leads to disoriented users, buried features, disjointed taxonomies, and high cognitive load. Navigation depth MUST be balanced: neither excessively deep ($> 4$ levels) nor overwhelmingly flat ($> 9$ primary menu choices exceeding Miller's Law).

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/navigation-flow-spec/SKILL.md`](../navigation-flow-spec/SKILL.md)
- Information Architecture: For the Web and Beyond (Rosenfeld, Morville, Arango)

## Isolation

`mutate` when generating or updating IA diagrams, sitemaps, or taxonomy schemas. Parent isolates via `spawn_worktree.py` before spawning `interaction-designer`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing navigation structures and domain models:
   `qmd search --format json --min-score 0.5 -n 5 "information architecture sitemap taxonomy navigation depth"` then `qmd get` matching files.
2. Conduct a content inventory and semantic classification:
   - Identify core entities, administrative zones, operational dashboards, and utility pages.
   - Group items into Mutually Exclusive, Collectively Exhaustive (MECE) categories.
3. Establish navigation hierarchy tiers:
   - **Tier 0 (Root / Global):** Primary application shell (Top navigation bar or primary sidebar: 4-7 items max).
   - **Tier 1 (Section Hub):** Category dashboards, list views, or workspace landing pages.
   - **Tier 2 (Item / Workspace):** Detailed records, editor workspaces, sub-category tabs.
   - **Tier 3 (Contextual Action / Deep Settings):** Specific sub-task sheets or nested configuration panes.
4. Author semantic RESTful URL routing schema:
   - Consistent kebab-case naming: `/workspaces/[workspaceId]/projects/[projectId]/settings`.
   - Clear distinction between collections, entities, and actions.
5. Audit navigation depth:
   - Calculate maximum click distance from the application root to critical workflows.
   - Flag any primary workflow requiring $> 3$ clicks as an architectural defect requiring shortcuts, search, or elevation.
6. Render the IA map using Mermaid flowcharts:
   ```mermaid
   flowchart TD
     AppRoot["Application Root (/)"]
     AppRoot --> Dashboard["Dashboard (/dashboard)"]
     AppRoot --> Projects["Projects (/projects)"]
     AppRoot --> DesignSystem["Design System (/design-system)"]
     AppRoot --> Settings["Settings (/settings)"]

     Projects --> ProjectList["All Projects (/projects)"]
     Projects --> ProjectDetail["Project Overview (/projects/:id)"]
     ProjectDetail --> ProjectTokens["Tokens (/projects/:id/tokens)"]
     ProjectDetail --> ProjectComponents["Components (/projects/:id/components)"]

     DesignSystem --> TokensCatalog["Token Catalog (/design-system/tokens)"]
     DesignSystem --> ComponentMatrix["Variant Matrix (/design-system/matrix)"]
     DesignSystem --> A11yAudit["A11y Reports (/design-system/a11y)"]

     Settings --> Profile["User Profile (/settings/profile)"]
     Settings --> Team["Team Permissions (/settings/team)"]
   ```
7. Verify wayfinding consistency:
   - Ensure breadcrumb trails match the declared hierarchy strictly.
   - Ensure active state indicators across navigation menus correspond to current URL routes.
8. Inspect documentation and schemas with ast-grep; compress large hierarchical charts with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill information-architecture-map --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic domain models only. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Complete sitemap hierarchy rendered in Mermaid. Navigation depth validated ($\le 3$ clicks for primary workflows, $\le 7$ root categories). Semantic URL hierarchy documented and aligned with wayfinding elements (breadcrumbs, menus).
