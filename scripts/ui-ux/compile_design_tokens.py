"""Lint and compile W3C DTCG design tokens to CSS variables, SCSS variables, and TypeScript token exports.

tags: [ui-ux, design-tokens, dtcg]
routing_hints: [tokens, css-variables, style-dictionary, typescript]

Rejects mixed legacy `value` keys and DTCG `$value`. Compiles a narrow v4-safe
subset (color, dimension, fontFamily, fontWeight, aliases) into CSS custom
properties (:root {...}), SCSS variables, Tailwind theme configuration, and
typed TypeScript constants and interfaces.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _synth import json_dump, repo_root, token_path  # noqa: E402

TOKEN_NAME = re.compile(r"^[A-Za-z0-9-]+$")
ALIAS_RE = re.compile(r"^\{([A-Za-z0-9.-]+)\}$")
ALLOWED_TYPES = {"color", "dimension", "fontFamily", "fontWeight"}


def _walk(node: Any, path: tuple[str, ...], errors: list[str], tokens: dict[str, dict[str, Any]]) -> None:
    """Recursively walk the token hierarchy, validating DTCG conventions."""
    if not isinstance(node, dict):
        errors.append(f"{'.'.join(path) or '<root>'}: expected object")
        return
    if "value" in node and "$value" in node:
        errors.append(f"{'.'.join(path)}: mixed legacy value and DTCG $value")
        return
    if "value" in node and "$value" not in node:
        errors.append(f"{'.'.join(path)}: legacy value key is not allowed (use $value)")
        return
    if "$value" in node:
        name = ".".join(path)
        typ = node.get("$type")
        if not typ:
            errors.append(f"{name}: $type missing")
            return
        if typ not in ALLOWED_TYPES:
            errors.append(f"{name}: $type {typ!r} not in fixture subset {sorted(ALLOWED_TYPES)}")
        tokens[name] = {
            "path": name,
            "type": typ,
            "value": node["$value"],
            "description": node.get("$description", ""),
        }
        return
    for key, child in node.items():
        if key.startswith("$"):
            continue
        if not TOKEN_NAME.match(key):
            errors.append(f"{'.'.join(path + (key,))}: invalid group/token name")
            continue
        _walk(child, path + (key,), errors, tokens)


def resolve(tokens: dict[str, dict[str, Any]]) -> list[str]:
    """Resolve token aliases like {color.action} to their concrete values, supporting multi-hop and cycle detection."""
    errors: list[str] = []
    state: dict[str, str] = {}  # "resolving", "resolved", "error"

    def _resolve_token(name: str, chain: list[str]) -> Any:
        rec = tokens[name]
        value = rec["value"]

        if not isinstance(value, str):
            rec["resolved"] = value
            state[name] = "resolved"
            return value

        match = ALIAS_RE.match(value)
        if not match:
            rec["resolved"] = value
            state[name] = "resolved"
            return value

        target = match.group(1)
        rec["alias_of"] = target

        if target not in tokens:
            errors.append(f"{name}: alias {{{target}}} is missing")
            rec["resolved"] = value
            state[name] = "error"
            return value

        if target in chain:
            cycle = " -> ".join(chain + [target])
            errors.append(f"{name}: circular alias reference detected ({cycle})")
            rec["resolved"] = value
            state[name] = "error"
            return value

        if state.get(target) == "resolved":
            resolved_val = tokens[target]["resolved"]
            rec["resolved"] = resolved_val
            state[name] = "resolved"
            return resolved_val

        if state.get(target) == "error":
            rec["resolved"] = value
            state[name] = "error"
            return value

        state[name] = "resolving"
        resolved_val = _resolve_token(target, chain + [target])
        rec["resolved"] = resolved_val
        if state.get(target) == "error":
            state[name] = "error"
        else:
            state[name] = "resolved"
        return resolved_val

    for name in list(tokens.keys()):
        if name not in state:
            _resolve_token(name, [name])

    return errors


def css_name(path: str) -> str:
    """Convert dot-separated token path to a CSS custom property name."""
    return "--" + path.replace(".", "-")


def render_css(tokens: dict[str, dict[str, Any]]) -> str:
    """Render tokens into CSS variables within a :root block."""
    lines = [":root {"]
    for name in sorted(tokens):
        rec = tokens[name]
        comment = f" /* {rec['description']} */" if rec.get("description") else ""
        lines.append(f"  {css_name(name)}: {rec['resolved']};{comment}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_scss(tokens: dict[str, dict[str, Any]]) -> str:
    """Render tokens into SCSS variable declarations."""
    lines = []
    for name in sorted(tokens):
        rec = tokens[name]
        lines.append(f"${name.replace('.', '-')}: {rec['resolved']};")
    lines.append("")
    return "\n".join(lines)


def render_tailwind(tokens: dict[str, dict[str, Any]]) -> str:
    """Render tokens into a Tailwind CSS theme extension dictionary."""
    colors = {
        name.split(".", 1)[-1]: rec["resolved"]
        for name, rec in tokens.items()
        if rec["type"] == "color"
    }
    spacing = {
        name.split(".", 1)[-1]: rec["resolved"]
        for name, rec in tokens.items()
        if rec["type"] == "dimension"
    }
    theme = {"theme": {"extend": {"colors": colors, "spacing": spacing}}}
    return json.dumps(theme, indent=2, sort_keys=True) + "\n"


def _build_nested_tree(tokens: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Build a nested dictionary mirroring the dot-separated token paths."""
    tree: dict[str, Any] = {}
    for name in sorted(tokens):
        parts = name.split(".")
        curr = tree
        for part in parts[:-1]:
            if not isinstance(curr.get(part), dict):
                curr[part] = {}
            curr = curr[part]
        curr[parts[-1]] = tokens[name]["resolved"]
    return tree


def render_typescript(tokens: dict[str, dict[str, Any]]) -> str:
    """Render strongly-typed TypeScript token exports and interfaces."""
    lines = [
        "/**",
        " * Design tokens compiled from W3C DTCG specification.",
        " * Generated by compile_design_tokens.py - do not edit directly.",
        " */",
        "",
        "export interface TokenDefinition {",
        "  readonly path: string;",
        "  readonly type: string;",
        "  readonly value: string | number;",
        "  readonly description?: string;",
        "}",
        "",
        "export const tokens = {",
    ]
    for name in sorted(tokens):
        rec = tokens[name]
        val_str = json.dumps(rec["resolved"])
        desc_comment = f" /* {rec['description']} */" if rec.get("description") else ""
        lines.append(f"  {json.dumps(name)}: {val_str},{desc_comment}")
    lines.extend([
        "} as const;",
        "",
        "export type TokenName = keyof typeof tokens;",
        "export type TokenValue = typeof tokens[TokenName];",
        "",
        "export const tokenMetadata: Record<TokenName, TokenDefinition> = {",
    ])
    for name in sorted(tokens):
        rec = tokens[name]
        meta_dict: dict[str, Any] = {
            "path": rec["path"],
            "type": rec["type"],
            "value": rec["resolved"],
        }
        if rec.get("description"):
            meta_dict["description"] = rec["description"]
        lines.append(f"  {json.dumps(name)}: {json.dumps(meta_dict)},")
    lines.extend([
        "} as const;",
        "",
    ])
    nested = _build_nested_tree(tokens)
    nested_json = json.dumps(nested, indent=2)
    lines.extend([
        "export const tokenTree = " + nested_json + " as const;",
        "",
        "export type TokenTree = typeof tokenTree;",
        "",
    ])
    return "\n".join(lines)


def compile_tokens(raw: dict[str, Any]) -> dict[str, Any]:
    """Compile raw DTCG JSON into CSS, SCSS, Tailwind, and TypeScript targets."""
    errors: list[str] = []
    tokens: dict[str, dict[str, Any]] = {}
    _walk(raw, (), errors, tokens)
    errors.extend(resolve(tokens))
    return {
        "ok": not errors,
        "errors": errors,
        "token_count": len(tokens),
        "tokens": tokens,
        "css": render_css(tokens) if not errors else "",
        "scss": render_scss(tokens) if not errors else "",
        "tailwind": render_tailwind(tokens) if not errors else "",
        "typescript": render_typescript(tokens) if not errors else "",
    }


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and execute token compilation."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to DTCG JSON token file (default scripts/ui-ux/fixtures/tokens/tokens.json)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Output directory to write tokens.css, tokens.scss, tailwind.theme.json, and tokens.ts",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compile tokens in memory without writing files to --out-dir",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root override path",
    )
    args = parser.parse_args(argv)
    root = args.repo_root.resolve() if args.repo_root else repo_root()
    src = args.input.resolve() if args.input else token_path(root)
    if not src.is_file():
        print(f"error: missing token file {src}", file=sys.stderr)
        return 2
    raw = json.loads(src.read_text(encoding="utf-8"))
    payload = compile_tokens(raw)
    payload["input"] = src.as_posix()
    if args.out_dir and payload["ok"] and not args.dry_run:
        out = args.out_dir.resolve()
        out.mkdir(parents=True, exist_ok=True)
        (out / "tokens.css").write_text(payload["css"], encoding="utf-8")
        (out / "tokens.scss").write_text(payload["scss"], encoding="utf-8")
        (out / "tailwind.theme.json").write_text(payload["tailwind"], encoding="utf-8")
        (out / "tokens.ts").write_text(payload["typescript"], encoding="utf-8")
        payload["written"] = [
            (out / "tokens.css").as_posix(),
            (out / "tokens.scss").as_posix(),
            (out / "tailwind.theme.json").as_posix(),
            (out / "tokens.ts").as_posix(),
        ]
    if args.json:
        print(json_dump({k: v for k, v in payload.items() if k != "tokens" or args.json}), end="")
    else:
        print(
            f"{'OK' if payload['ok'] else 'FAIL'} tokens count={payload['token_count']} "
            f"errors={len(payload['errors'])}"
        )
        for err in payload["errors"]:
            print(f"  - {err}")
        if args.dry_run:
            print("dry-run: compile only; no --out-dir writes")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
