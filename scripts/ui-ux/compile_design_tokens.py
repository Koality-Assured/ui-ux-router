"""Lint and compile W3C DTCG design tokens to CSS/SCSS/Tailwind snippets.

tags: [ui-ux, design-tokens, dtcg]
routing_hints: [tokens, css-variables, style-dictionary]

Rejects mixed legacy `value` keys and DTCG `$value`. Compiles a narrow v4-safe
subset (color, dimension, aliases). Not a full Style Dictionary clone.
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
    errors: list[str] = []
    for name, rec in tokens.items():
        value = rec["value"]
        if isinstance(value, str):
            match = ALIAS_RE.match(value)
            if match:
                target = match.group(1)
                if target not in tokens:
                    errors.append(f"{name}: alias {{{target}}} is missing")
                rec["resolved"] = tokens.get(target, {}).get("value", value)
                rec["alias_of"] = target
            else:
                rec["resolved"] = value
        else:
            rec["resolved"] = value
    return errors


def css_name(path: str) -> str:
    return "--" + path.replace(".", "-")


def render_css(tokens: dict[str, dict[str, Any]]) -> str:
    lines = [":root {"]
    for name in sorted(tokens):
        rec = tokens[name]
        comment = f" /* {rec['description']} */" if rec.get("description") else ""
        lines.append(f"  {css_name(name)}: {rec['resolved']};{comment}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_scss(tokens: dict[str, dict[str, Any]]) -> str:
    lines = []
    for name in sorted(tokens):
        rec = tokens[name]
        lines.append(f"${name.replace('.', '-')}: {rec['resolved']};")
    lines.append("")
    return "\n".join(lines)


def render_tailwind(tokens: dict[str, dict[str, Any]]) -> str:
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


def compile_tokens(raw: dict[str, Any]) -> dict[str, Any]:
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="DTCG JSON (default scripts/ui-ux/fixtures/tokens/tokens.json)")
    parser.add_argument("--out-dir", type=Path, help="Write tokens.css / tokens.scss / tailwind.theme.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", type=Path)
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
        payload["written"] = [
            (out / "tokens.css").as_posix(),
            (out / "tokens.scss").as_posix(),
            (out / "tailwind.theme.json").as_posix(),
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
