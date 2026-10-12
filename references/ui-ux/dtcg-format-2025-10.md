---
doc_kind: reference
canonical_id: dtcg-format-2025-10
topics: [design-tokens, dtcg, w3c, style-dictionary]
last_verified: "2026-10-12"
---

# W3C Design Tokens Community Group (DTCG) Format Module 2025.10

## Specification status

W3C Community Group Final Report, 28 October 2025.
The DTCG Format Module provides the canonical interchange standard for design tokens between Figma, Style Dictionary, web, Android, and iOS.

## Syntax requirements

1. **Token declaration**:
   Every token must declare `$value`.
   `$type` is required on the token itself or inherited from the nearest parent group:
   ```json
   {
     "color": {
       "$type": "color",
       "primary": {
         "$value": "#0055ff",
         "$description": "Brand primary accessible blue"
       }
     }
   }
   ```

2. **Reserved keys**:
   - `$value`: Token data.
   - `$type`: Token type string.
   - `$description`: Human documentation.
   - `$extensions`: Tooling or platform-specific metadata.
   - `$deprecated`: Flag or migration instructions.

3. **Aliases and references**:
   Curly brace syntax: `"{group.subgroup.token_name}"`.
   Example: `"$value": "{color.primary}"`.

4. **Supported base types**:
   `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`, `string`.
   Composite types: `shadow`, `typography`, `border`, `transition`, `gradient`.
