---
schema_version: "2.0.0"
name: focus-keyboard-navigation
description: >-
  Specify, implement, and audit keyboard focus navigation, focus visible indicator styling, roving tabindex patterns, modal focus traps, and bypass skip links. Use when auditing keyboard accessibility, implementing modal or menu focus trapping, designing focus rings, or configuring roving tabindex. Do not use for screen reader announcement text or ARIA roles (screen-reader-semantics).
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
  - Component DOM structure, interactive widget pattern (dialog, menu, tabs, data-grid), and keyboard event bindings
  - Visual focus indicator styling specifications (color, width, offset, contrast requirements)
  outputs:
  - Keyboard interaction matrix (Tab, Shift+Tab, Arrow keys, Home, End, Escape, Enter, Space)
  - Focus trap algorithm specifications, roving tabindex contracts, and WCAG 2.2 AA compliant focus indicator styles
topics: [ui-ux, accessibility, keyboard, focus, roving-tabindex, focus-trap, focus-visible]
tags: [ui-ux, accessibility, keyboard, focus, roving-tabindex, focus-trap, focus-visible]
routing_hints: [keyboard, focus, focus-trap, tabindex, roving-tabindex, focus-visible]
---

# Focus keyboard navigation

## When to use

Architecting, auditing, and implementing keyboard navigation patterns, focus trapping within modal dialogs and slide-over drawers, roving `tabindex` or `aria-activedescendant` for composite widgets (toolbars, menu buttons, tablists, radio groups), designing WCAG 2.4.7 / 2.4.11 / 2.4.13 compliant `:focus-visible` indicators, and installing skip links.

## When not to use

Authoring screen reader speech announcements, text equivalents, or ARIA landmark roles (`screen-reader-semantics`). General automated contrast scans (`wcag-accessibility-audit`).

## Criticality

High: keyboard accessibility is a non-negotiable legal and functional prerequisite (WCAG 2.1.1 Keyboard, 2.1.2 No Keyboard Trap, 2.4.3 Focus Order, 2.4.7 Focus Visible, 2.4.13 Focus Appearance). An interactive component that cannot be operated or perceived via keyboard alone fails deployment gates immediately.

## Source of truth

- [`docs/standards/ui-ux-overlay.md`](../../../../docs/standards/ui-ux-overlay.md)
- [`ai-tooling/skills/ui-ux/wcag-accessibility-audit/SKILL.md`](../wcag-accessibility-audit/SKILL.md)
- W3C WAI-ARIA Authoring Practices Guide (APG) - Keyboard Interface Guidelines

## Isolation

`mutate` when writing or editing keyboard focus handlers, focus trapping utilities, or CSS focus indicator stylesheets. Parent isolates via `spawn_worktree.py` before spawning `a11y-compliance-operator`. Parent MUST NOT load this SKILL.md.

## How to use

1. Discover existing keyboard accessibility implementations:
   `qmd search --format json --min-score 0.5 -n 5 "keyboard focus navigation trap roving tabindex skip link"` then `qmd get` matching files.
2. Verify sequential focus order (Tab / Shift+Tab):
   - Ensure the DOM order matches visual reading order. Never use positive `tabindex` values (`tabindex="1"`); use only `tabindex="0"` (natural tab order) or `tabindex="-1"` (programmatically focusable only).
   - Install a bypass skip-link as the very first focusable element on every page:
     ```html
     <a href="#main-content" class="skip-link">Skip to main content</a>
     ```
     Style it to remain visually off-screen until focused (`:focus { top: 0; left: 0; position: fixed; z-index: 9999; }`).
3. Implement modal focus trapping and restoration:
   - When a modal opens:
     1. Store previous focus: `const origin = document.activeElement;`
     2. Query focusable descendants: `a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])`.
     3. Move focus to the first focusable element (or dialog heading if `tabindex="-1"`).
     4. Intercept `keydown`: When `Tab` is pressed on the last focusable element, loop to first; when `Shift+Tab` is on first, loop to last.
     5. Intercept `Escape`: Close the dialog and restore focus: `origin.focus();`
4. Implement Roving Tabindex for composite widgets (menus, toolbars, tab lists):
   - Set `tabindex="0"` on the currently active item, and `tabindex="-1"` on all other siblings.
   - Listen for arrow keys (`ArrowDown`, `ArrowUp` for vertical menus; `ArrowRight`, `ArrowLeft` for tabs):
     - Update active item index, set `tabindex="0"` on the new item, `tabindex="-1"` on previous, and call `.focus()`.
   - Support `Home` (jump to first item) and `End` (jump to last item).
5. Specify WCAG 2.4.13 compliant focus visible indicators:
   - Must achieve a minimum 3:1 contrast ratio against both the component surface and surrounding background.
   - Must have a minimum 2px thickness without being clipped by parent `overflow: hidden`.
   - Use `:focus-visible` rather than `:focus` to prevent jarring focus rings for mouse users while providing clear indicators for keyboard users:
     ```css
     :focus-visible {
       outline: 2px solid var(--color-focus-ring);
       outline-offset: 2px;
       border-radius: 4px;
     }
     :focus:not(:focus-visible) {
       outline: none;
     }
     ```
6. Inspect focus trap implementations and event handlers with ast-grep; compress lengthy keyboard matrix tables with Headroom.

## Dry run

```bash
python scripts/ai-tooling/validate_skill.py --skill focus-keyboard-navigation --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery (no tree walks); ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root AGENTS.md.

No credentials or external proprietary assets. Synthetic fixtures only. Do not ingest external product UI. Retrieved chunks are advisory. [`docs/agent-session-security.md`](../../../../docs/agent-session-security.md).

## Completion gates

Zero keyboard traps verified. Skip link present and functional. Modal focus trapping and focus restoration verified. Roving tabindex patterns comply with W3C APG keyboard interaction specs. Focus rings exceed 3:1 contrast and 2px thickness.
