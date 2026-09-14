"""WCAG 2.2 AA accessibility audit for synthetic UI fixtures.

tags: [ui-ux, accessibility, wcag, axe-core]
routing_hints: [contrast, keyboard-trap, axe, focus-order]

Stdlib auditor catches planted contrast, target-size, unlabeled control, and
keyboard-trap cases. Optional --engine axe shells to npx @axe-core/cli when Node
is available. Axe output is advisory and is not WCAG certification.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _synth import (  # noqa: E402
    AA_CONTRAST,
    MIN_TARGET_PX,
    contrast_ratio,
    json_dump,
    list_component_html,
    parse_fixture,
    repo_root,
)

AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa"]


def audit_html(html: str, name: str) -> list[dict[str, object]]:
    parsed = parse_fixture(html)
    findings: list[dict[str, object]] = []
    if parsed.keyboard_trap:
        findings.append(
            {
                "id": "keyboard-trap",
                "impact": "critical",
                "fixture": name,
                "help": "Tab key is prevented or data-keyboard-trap is set",
            }
        )
    if not parsed.has_main and not parsed.has_dialog:
        findings.append(
            {
                "id": "landmark-missing",
                "impact": "moderate",
                "fixture": name,
                "help": "No main landmark or dialog role",
            }
        )
    if parsed.unlabeled_controls:
        findings.append(
            {
                "id": "control-unlabeled",
                "impact": "serious",
                "fixture": name,
                "help": f"{parsed.unlabeled_controls} input(s) lack label or aria-label",
            }
        )
    for box in parsed.boxes:
        ratio = round(contrast_ratio(box.fg, box.bg), 2)
        if ratio < AA_CONTRAST:
            findings.append(
                {
                    "id": "contrast",
                    "impact": "serious",
                    "fixture": name,
                    "help": f"{box.role} contrast {ratio}:1 < {AA_CONTRAST}:1",
                    "fg": list(box.fg),
                    "bg": list(box.bg),
                }
            )
        if box.role in {"button", "textbox", "input"} and (
            box.w < MIN_TARGET_PX or box.h < MIN_TARGET_PX
        ):
            findings.append(
                {
                    "id": "target-size",
                    "impact": "serious",
                    "fixture": name,
                    "help": f"{box.role} {box.w}x{box.h}px below WCAG 2.5.8 {MIN_TARGET_PX}px",
                }
            )
    return findings


def run_axe(html_path: Path) -> dict[str, object]:
    npx = shutil.which("npx")
    if not npx:
        return {"ok": False, "engine": "axe", "error": "npx not on PATH"}
    cmd = [
        npx,
        "--yes",
        "@axe-core/cli",
        str(html_path),
        "--tags",
        ",".join(AXE_TAGS),
        "--stdout",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "engine": "axe",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-2000:],
    }


def run(*, root: Path, engine: str, fail_on: set[str]) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    axe_rows: list[dict[str, object]] = []
    for html_path in list_component_html(root):
        html = html_path.read_text(encoding="utf-8")
        findings.extend(audit_html(html, html_path.name))
        if engine == "axe":
            axe_rows.append({"fixture": html_path.name, **run_axe(html_path)})
    gated = [item for item in findings if item["id"] in fail_on]
    payload = {
        "ok": not gated,
        "engine": engine,
        "wcag": "2.2 AA (automated subset; not certification)",
        "axe_tags": AXE_TAGS,
        "finding_count": len(findings),
        "gated_count": len(gated),
        "findings": findings,
    }
    if axe_rows:
        payload["axe"] = axe_rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("synthetic", "axe"), default="synthetic")
    parser.add_argument(
        "--fail-on",
        default="contrast,keyboard-trap,control-unlabeled,target-size",
        help="Comma-separated finding ids that fail the process",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Same as default; never writes")
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve() if args.repo_root else repo_root()
    fail_on = {part.strip() for part in args.fail_on.split(",") if part.strip()}
    payload = run(root=root, engine=args.engine, fail_on=fail_on)
    if args.json:
        print(json_dump(payload), end="")
    else:
        print(
            f"{'OK' if payload['ok'] else 'FAIL'} a11y engine={payload['engine']} "
            f"findings={payload['finding_count']} gated={payload['gated_count']}"
        )
        for item in payload["findings"]:
            print(f"  {item['impact']:10} {item['id']:20} {item['fixture']}: {item['help']}")
        if args.dry_run:
            print("dry-run: no files written")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
