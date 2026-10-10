---
schema_version: "2.0.0"
name: navigation-flow-spec
description: >-
  Specify, map, and validate interactive navigation flows, view transition lifecycles, modal and drawer stack hierarchies, and history state contracts. Use when specifying navigation patterns, modal/drawer interaction stacks, multi-step wizard flows, or view transition states. Do not use for top-level sitemap or content taxonomy mapping (information-architecture-map).
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
  - User journey steps, view transition triggers, modal/drawer hierarchy, and route parameter definitions
  - Target navigation framework (HTML5 History API, SPA router, or View Transitions API)
  outputs:
  - Navigation flow specification document with state-machine transition diagrams, back-stack rules, and focus restoration contracts
  - URL synchronization schema and dismissible layer lifecycle rules (Escape key, backdrop click, popstate)
topics: [ui-ux, navigation, flow-spec, view-transitions, modal-stack, state-machine]
tags: [ui-ux, navigation, flow-spec, view-transitions, modal-stack, state-machine]
routing_hints: [navigation, flow, view-transitions, route-hierarchy, modal-stack]
---

# Navigation flow spec

## When to use

Authoring detailed interaction specifications for user journey flows, view transition lifecycles (browser View Transition API), modal/drawer back-stack hierarchies, multi-step wizards, tab bar navigation, deep linking URL synchronization, and scroll/focus restoration across route changes.

## When not to use

Mapping high-level information architecture, taxonomy, or content grouping across an entire application (`information-architecture-map`). Auditing keyboard-only focus trapping inside an active dialog (`focus-keyboard-navigation`).

## Criticality

High: ambiguous navigation flows create dead ends, broken browser history (broken back button), orphaned modal overlays, and lost user input in multi-step processes. Every navigable state MUST be deterministic, bookmarkable where appropriate, and maintain predictable stack unwinding.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/information-architecture-map/SKILL.md`](../information-architecture-map/SKILL.md)
- W3C View Transitions API Level 1 & HTML Living Standard (History and Navigation)

## Isolation

`mutate` when writing or updating navigation flow specifications, state transition diagrams, or route contract documents. Parent isolates via `spawn_worktree.py` before spawning `interaction-designer`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing interaction specifications and route standards:
   `qmd search --format json --min-score 0.5 -n 5 "navigation flow spec view transition modal stack"` then `qmd get` matching files.
2. Formalize navigation flow as a finite-state machine (FSM):
   - **States:** `Idle/ListView`, `DetailView`, `EditModal`, `ConfirmDiscardDialog`, `Submitting`, `SuccessNotification`.
   - **Transitions:** User actions (`CLICK_ITEM`, `PRESS_EDIT`, `CLICK_BACK`, `PRESS_ESCAPE`), system events (`FETCH_SUCCESS`, `NETWORK_TIMEOUT`).
3. Define modal and drawer stack lifecycle rules:
   - **LIFO (Last-In-First-Out) dismissal:** The topmost overlay absorbs the `Escape` key event and backdrop clicks. Subordinate layers remain inert (`inert` attribute applied).
   - **Scroll locking:** When an overlay mounts, apply `overflow: hidden` to `document.body` while compensating for scrollbar width shift (`scrollbar-gutter: stable`).
   - **Focus restoration:** Store a reference to the active element (`document.activeElement`) prior to opening the layer; restore focus explicitly upon dismiss.
4. Specify URL synchronization contracts:
   - Determine state representation: Route path (`/projects/:id`), query parameter (`?view=grid&filter=active`), or transient session state.
   - Guard destructive exits: If unsaved state exists, register a `beforeunload` or router navigation guard prompting user confirmation.
5. Author modern View Transition specifications:
   - Assign semantic `view-transition-name` tokens to shared persistent elements (e.g. hero card image transitioning to detail header):
     ```css
     .card-thumbnail { view-transition-name: item-image-123; }
     ::view-transition-group(item-image-123) {
       animation-duration: 250ms;
       animation-timing-function: cubic-bezier(0.4, 0.0, 0.2, 1);
     }
     ```
6. Model navigation paths using Mermaid state diagrams:
   ```mermaid
   stateDiagram-v2
     [*] --> BrowseCatalog
     BrowseCatalog --> ItemDetail: Select Item (pushState)
     ItemDetail --> EditModal: Open Edit (stack push)
     EditModal --> ItemDetail: Save / Dismiss (stack pop, restore focus)
     ItemDetail --> BrowseCatalog: Back (popstate)
   ```
7. Use ast-grep for structured code/state inspection; compress bulky transition specs with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill navigation-flow-spec --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic navigation patterns only. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Complete navigation state diagram generated. Overlay stack order (LIFO), back button behavior, focus restoration points, and URL parameter mappings documented with zero ambiguous branches.
