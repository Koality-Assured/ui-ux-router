---
doc_kind: reference
canonical_id: wcag-2-2-success-criteria
topics: [accessibility, wcag-2-2, wai, compliance]
last_verified: "2026-10-12"
---

# W3C WCAG 2.2 accessibility standard reference

## Overview and normative status

W3C Recommendation 05 October 2023 (updated 12 December 2024). ISO/IEC 40500:2025.
WCAG 2.2 is backward-compatible with 2.1 and 2.0. Meeting WCAG 2.2 Level AA satisfies all antecedent Level AA criteria.

## Nine additive success criteria in WCAG 2.2

| Success Criterion | Level | Summary & Verification Rule |
| :--- | :---: | :--- |
| **2.4.11 Focus Not Obscured (Minimum)** | AA | When a component receives keyboard focus, it is not entirely hidden by author-created content (e.g. sticky headers, floating banners). |
| **2.4.12 Focus Not Obscured (Enhanced)** | AAA | No part of the focused component is hidden by author content. |
| **2.4.13 Focus Appearance** | AAA | Focus indicator has at least a 2px solid perimeter or 3:1 contrast ratio against unfocused state. |
| **2.5.7 Dragging Movements** | AA | All functionality requiring dragging can be operated by a single pointer without dragging (e.g. tapping increment buttons or modal selector). |
| **2.5.8 Target Size (Minimum)** | AA | Pointer target size is at least 24 by 24 CSS pixels, except where spaced sufficiently from adjacent targets, inline in text, or essential. |
| **3.2.6 Consistent Help** | A | Help mechanisms (contact info, chat, FAQ) appear in the same relative order across pages. |
| **3.3.7 Redundant Entry** | A | Information previously entered in the same session is auto-populated or available for selection. |
| **3.3.8 Accessible Authentication (Minimum)** | AA | Authentication does not rely on cognitive function tests (memorizing passwords, solving puzzles) unless an alternative or paste assistance is provided. |
| **3.3.9 Accessible Authentication (Enhanced)** | AAA | No cognitive function test or object recognition required for login. |

## Deprecations in 2.2

- **4.1.1 Parsing** is obsolete and removed from WCAG 2.2 as modern HTML parsers handle well-formedness natively.
