---
schema_version: "2.0.0"
name: screen-reader-semantics
description: >-
  Specify, inspect, and validate ARIA semantic roles, landmark regions, accessible name computation (AccName 1.2), live regions, and screen-reader utility patterns. Use when specifying ARIA attributes, auditing screen reader announcements, fixing landmark coverage, or defining accessible naming. Do not use for keyboard focus trapping or roving tabindex (focus-keyboard-navigation).
owner_agent: a11y-compliance-operator
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
  - Component HTML templates, interactive widget patterns, and dynamic content announcement requirements
  - Target assistive technology profile (NVDA, JAWS, VoiceOver, TalkBack) and ARIA version (WAI-ARIA 1.2/1.3)
  outputs:
  - ARIA semantic role mappings, accessible name / description source tables, and landmark partition specifications
  - Dynamic live region policies (aria-live, aria-atomic) and screen-reader-only utility classes
topics: [ui-ux, accessibility, screen-reader, aria, accname, landmarks, aria-live]
tags: [ui-ux, accessibility, screen-reader, aria, accname, landmarks, aria-live]
routing_hints: [screen-reader, aria, semantics, landmarks, accname, aria-live]
---

# Screen reader semantics

## When to use

Authoring and validating ARIA semantic structures, ensuring complete landmark region coverage (`banner`, `main`, `navigation`, `complementary`, `contentinfo`, `search`, `region`), computing accessible names and descriptions (W3C AccName 1.2 algorithm), orchestrating dynamic announcements with `aria-live` regions, and verifying screen-reader-only utility patterns (`.sr-only`).

## When not to use

Keyboard focus trapping, tab order sequencing, or `:focus-visible` styling (`focus-keyboard-navigation`). Running automated contrast and synthetic axe checks (`wcag-accessibility-audit`).

## Criticality

High: missing or incorrect ARIA roles, unlabelled icon buttons, or redundant landmarks render applications unusable for screen reader users (WCAG 4.1.2 Name, Role, Value; WCAG 1.3.1 Info and Relationships). The First Rule of ARIA MUST be upheld: do not use ARIA when native HTML can achieve the same semantic outcome.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/wcag-accessibility-audit/SKILL.md`](../wcag-accessibility-audit/SKILL.md)
- W3C WAI-ARIA 1.2 Specification & W3C Accessible Name and Description Computation 1.2

## Isolation

`mutate` when updating component templates, HTML fixtures, or accessibility semantic specifications. Parent isolates via `spawn_worktree.py` before spawning `a11y-compliance-operator`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing accessibility fixtures and standards:
   `qmd search --format json --min-score 0.5 -n 5 "aria screen reader semantics accname landmarks live region"` then `qmd get` matching files.
2. Apply the First Rule of ARIA:
   - Prefer native HTML5 elements (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`, `<button>`, `<dialog>`) over generic `<div>` elements with ARIA roles.
   - Use ARIA roles only when enhancing or polyfilling custom widgets where native semantics do not exist.
3. Validate landmark region coverage:
   - Ensure every perceptible part of the page is enclosed within a structural landmark:
     - `header` / `role="banner"` (top application header)
     - `nav` / `role="navigation"` (primary, breadcrumb, or pagination nav)
     - `main` / `role="main"` (unique core content area)
     - `aside` / `role="complementary"` (contextual sidebar)
     - `footer` / `role="contentinfo"` (copyright and legal links)
     - `form[role="search"]` (search input zone)
   - When multiple landmarks of the same type exist (e.g. multiple `<nav>`), differentiate them with explicit `aria-label` (e.g. `aria-label="Main Navigation"`, `aria-label="Breadcrumbs"`).
4. Calculate accessible names using the AccName 1.2 precedence:
   - 1st: `aria-labelledby="[id]"` (highest precedence, references another element's visible text).
   - 2nd: `aria-label="[string]"` (direct override, use for icon-only buttons or ambiguous controls).
   - 3rd: Native text content (e.g. `<button>Save</button>`).
   - 4th: Form label associations (`<label for="[id]">`).
   - 5th: Fallback attributes (`alt`, `title`). Never rely solely on `placeholder` or `title` as the sole accessible name.
5. Orchestrate dynamic live regions for async state updates:
   - **`aria-live="polite"`:** Standard status updates, non-critical background notifications, search result counts. The screen reader finishes its current utterance before reading.
   - **`aria-live="assertive"`:** Critical errors, security session timeouts, urgent system alerts. Interrupts current speech immediately.
   - Combine with `aria-atomic="true"` to ensure the complete message is announced rather than just the changed diff.
6. Verify off-screen accessibility utility styling:
   ```css
   .sr-only {
     position: absolute;
     width: 1px;
     height: 1px;
     padding: 0;
     margin: -1px;
     overflow: hidden;
     clip: rect(0, 0, 0, 0);
     white-space: nowrap;
     border: 0;
   }
   ```
7. Use ast-grep to locate missing ARIA labels, unlabelled buttons, or illegal role combinations; compress accessibility trees with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill screen-reader-semantics --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic fixtures only. Do not ingest external product UI. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

All interactive controls have verified non-empty accessible names. Complete landmark coverage verified (no orphan content outside landmarks). Live regions properly tagged with polite/assertive priorities.
