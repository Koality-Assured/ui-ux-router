"""WCAG 2.2 AA/AAA accessibility audit and APCA contrast testing with CVD simulation.

tags: [ui-ux, accessibility, wcag, apca, axe-core]
routing_hints: [contrast, keyboard-trap, axe, focus-order, touch-target, color-blindness]

Evaluates synthetic HTML fixtures and raw color pairs against WCAG 2.2 Level
AA and AAA criteria (contrast, keyboard-trap, touch target size, unlabeled
controls). Calculates WCAG contrast ratios and Advanced Perceptual Contrast
Algorithm (APCA) scores, and simulates Color Vision Deficiency (CVD) matrices
(protanopia, deuteranopia, tritanopia, achromatopsia).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _synth import (  # noqa: E402
    contrast_ratio,
    json_dump,
    list_component_html,
    parse_fixture,
    parse_hex,
    repo_root,
)

AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa"]

# WCAG 2.2 Contrast Ratio Thresholds
AA_CONTRAST = 4.5
AA_CONTRAST_LARGE = 3.0
AAA_CONTRAST = 7.0
AAA_CONTRAST_LARGE = 4.5

# WCAG 2.2 Target Size Thresholds (in CSS pixels)
MIN_TARGET_PX_AA = 24  # WCAG 2.2 Success Criterion 2.5.8 (Target Size - Minimum)
MIN_TARGET_PX_AAA = 44  # WCAG 2.1/2.2 Success Criterion 2.5.5 (Target Size - Enhanced)

# 3x3 Transformation matrices for Color Vision Deficiency (CVD) simulations
CVD_MATRICES: dict[str, list[list[float]]] = {
    "protanopia": [
        [0.56667, 0.43333, 0.0],
        [0.55833, 0.44167, 0.0],
        [0.0, 0.24167, 0.75833],
    ],
    "deuteranopia": [
        [0.625, 0.375, 0.0],
        [0.70, 0.30, 0.0],
        [0.0, 0.30, 0.70],
    ],
    "tritanopia": [
        [0.95, 0.05, 0.0],
        [0.0, 0.43333, 0.56667],
        [0.0, 0.475, 0.525],
    ],
    "achromatopsia": [
        [0.299, 0.587, 0.114],
        [0.299, 0.587, 0.114],
        [0.299, 0.587, 0.114],
    ],
}


def srgb_to_y(rgb: tuple[int, int, int]) -> float:
    """Convert an sRGB tuple (0-255) to luminance Y using APCA exponent."""
    def to_linear(val: int) -> float:
        return (val / 255.0) ** 2.4
    r, g, b = (to_linear(c) for c in rgb)
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    if y < 0.022:
        y += (0.022 - y) ** 1.414
    return y


def apca_contrast(txt_rgb: tuple[int, int, int], bg_rgb: tuple[int, int, int]) -> float:
    """Calculate Advanced Perceptual Contrast Algorithm (APCA) contrast score."""
    txt_y = srgb_to_y(txt_rgb)
    bg_y = srgb_to_y(bg_rgb)
    if abs(txt_y - bg_y) < 0.0005:
        return 0.0
    if bg_y > txt_y:
        sapc = (bg_y ** 0.56 - txt_y ** 0.57) * 1.14
        output = (sapc - 0.027) * 100.0 if sapc > 0.027 else 0.0
    else:
        sapc = (bg_y ** 0.65 - txt_y ** 0.62) * 1.14
        output = (sapc + 0.027) * 100.0 if sapc < -0.027 else 0.0
    return round(output, 2)


def evaluate_apca(score: float) -> dict[str, Any]:
    """Evaluate APCA contrast score and return readability tier and recommendations."""
    abs_score = abs(score)
    if abs_score >= 90:
        rating = "preferred-body"
        desc = "Preferred for fluent body text reading across all font weights"
    elif abs_score >= 75:
        rating = "minimum-body"
        desc = "Minimum for body text >= 16px normal or 14px bold"
    elif abs_score >= 60:
        rating = "large-text"
        desc = "Acceptable for large content text >= 24px normal or 18px bold"
    elif abs_score >= 45:
        rating = "display-large"
        desc = "Acceptable for display headings >= 36px or primary icons"
    elif abs_score >= 30:
        rating = "non-text"
        desc = "Subtle borders, placeholder, or disabled elements only"
    else:
        rating = "fail"
        desc = "Insufficient contrast for readable content"
    return {
        "score": score,
        "absolute_score": abs_score,
        "rating": rating,
        "description": desc,
        "accessible_body": abs_score >= 75,
        "accessible_large": abs_score >= 60,
    }


def evaluate_wcag_contrast(
    ratio: float,
    level: str = "AA",
    is_large_text: bool = False,
) -> bool:
    """Check if contrast ratio satisfies WCAG Level AA or AAA thresholds."""
    lvl = level.upper()
    if lvl == "AAA":
        threshold = AAA_CONTRAST_LARGE if is_large_text else AAA_CONTRAST
    else:
        threshold = AA_CONTRAST_LARGE if is_large_text else AA_CONTRAST
    return ratio >= threshold


def verify_touch_target_size(
    width: int,
    height: int,
    level: str = "AA",
) -> dict[str, Any]:
    """Verify element dimensions against WCAG touch target size requirements."""
    min_px = MIN_TARGET_PX_AAA if level.upper() == "AAA" else MIN_TARGET_PX_AA
    passes = width >= min_px and height >= min_px
    return {
        "width": width,
        "height": height,
        "min_required": min_px,
        "level": level.upper(),
        "pass": passes,
        "wcag_criterion": "2.5.5 (AAA)" if level.upper() == "AAA" else "2.5.8 (AA)",
    }


def simulate_cvd(rgb: tuple[int, int, int], deficiency: str) -> tuple[int, int, int]:
    """Transform an sRGB color using standard 3x3 CVD simulation matrices."""
    matrix = CVD_MATRICES.get(deficiency.lower())
    if not matrix:
        raise ValueError(f"Unknown deficiency {deficiency!r}. Supported: {list(CVD_MATRICES)}")
    r, g, b = rgb
    sim_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
    sim_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
    sim_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b
    return (
        max(0, min(255, round(sim_r))),
        max(0, min(255, round(sim_g))),
        max(0, min(255, round(sim_b))),
    )


def evaluate_color_blindness(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
) -> dict[str, dict[str, Any]]:
    """Evaluate contrast ratios and APCA scores under simulated color blindness."""
    results: dict[str, dict[str, Any]] = {}
    for condition in sorted(CVD_MATRICES):
        sim_fg = simulate_cvd(fg, condition)
        sim_bg = simulate_cvd(bg, condition)
        ratio = round(contrast_ratio(sim_fg, sim_bg), 2)
        apca = apca_contrast(sim_fg, sim_bg)
        results[condition] = {
            "sim_fg": list(sim_fg),
            "sim_bg": list(sim_bg),
            "contrast_ratio": ratio,
            "apca_score": apca,
            "wcag_aa_pass": ratio >= AA_CONTRAST,
            "wcag_aaa_pass": ratio >= AAA_CONTRAST,
        }
    return results


def compute_contrast_matrix(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
) -> dict[str, Any]:
    """Compute complete WCAG 2.2 contrast, APCA score, and CVD simulations for color pair."""
    ratio = round(contrast_ratio(fg, bg), 2)
    apca = apca_contrast(fg, bg)
    apca_eval = evaluate_apca(apca)
    cvd = evaluate_color_blindness(fg, bg)
    return {
        "fg": list(fg),
        "bg": list(bg),
        "wcag_contrast_ratio": ratio,
        "wcag_aa_normal_pass": ratio >= AA_CONTRAST,
        "wcag_aa_large_pass": ratio >= AA_CONTRAST_LARGE,
        "wcag_aaa_normal_pass": ratio >= AAA_CONTRAST,
        "wcag_aaa_large_pass": ratio >= AAA_CONTRAST_LARGE,
        "apca": apca_eval,
        "color_blindness_simulation": cvd,
    }


def audit_html(html: str, name: str, level: str = "AA") -> list[dict[str, object]]:
    """Audit single HTML fixture for keyboard-trap, landmarks, unlabeled controls, contrast, and target size."""
    parsed = parse_fixture(html)
    findings: list[dict[str, object]] = []
    lvl = level.upper()
    contrast_threshold = AAA_CONTRAST if lvl == "AAA" else AA_CONTRAST
    min_target = MIN_TARGET_PX_AAA if lvl == "AAA" else MIN_TARGET_PX_AA

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
        apca = apca_contrast(box.fg, box.bg)
        if ratio < contrast_threshold:
            findings.append(
                {
                    "id": "contrast",
                    "impact": "serious",
                    "fixture": name,
                    "help": f"{box.role} contrast {ratio}:1 < {contrast_threshold}:1 ({lvl})",
                    "fg": list(box.fg),
                    "bg": list(box.bg),
                    "ratio": ratio,
                    "apca_score": apca,
                    "color_blindness": evaluate_color_blindness(box.fg, box.bg),
                }
            )
        if box.role in {"button", "textbox", "input", "select"} and (
            box.w < min_target or box.h < min_target
        ):
            findings.append(
                {
                    "id": "target-size",
                    "impact": "serious",
                    "fixture": name,
                    "help": f"{box.role} {box.w}x{box.h}px below WCAG {min_target}px ({lvl})",
                    "width": box.w,
                    "height": box.h,
                    "min_required": min_target,
                }
            )
    return findings


def run_axe(html_path: Path) -> dict[str, object]:
    """Execute optional axe-core CLI analysis when npx is available."""
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


def run(
    *,
    root: Path,
    engine: str,
    fail_on: set[str],
    level: str = "AA",
) -> dict[str, object]:
    """Run accessibility audit across all fixtures in repository."""
    findings: list[dict[str, object]] = []
    axe_rows: list[dict[str, object]] = []
    for html_path in list_component_html(root):
        html = html_path.read_text(encoding="utf-8")
        findings.extend(audit_html(html, html_path.name, level=level))
        if engine == "axe":
            axe_rows.append({"fixture": html_path.name, **run_axe(html_path)})
    gated = [item for item in findings if item["id"] in fail_on]
    payload: dict[str, object] = {
        "ok": not gated,
        "engine": engine,
        "level": level.upper(),
        "wcag": f"2.2 {level.upper()} (automated subset; not certification)",
        "axe_tags": AXE_TAGS,
        "finding_count": len(findings),
        "gated_count": len(gated),
        "findings": findings,
    }
    if axe_rows:
        payload["axe"] = axe_rows
    return payload


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and execute accessibility audit."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--engine",
        choices=("synthetic", "axe"),
        default="synthetic",
        help="Audit engine: synthetic (stdlib) or axe (@axe-core/cli)",
    )
    parser.add_argument(
        "--level",
        choices=("AA", "AAA", "aa", "aaa"),
        default="AA",
        help="WCAG conformance level threshold (default AA: 4.5:1 contrast, 24px target)",
    )
    parser.add_argument(
        "--fail-on",
        default="contrast,keyboard-trap,control-unlabeled,target-size",
        help="Comma-separated finding IDs that fail the process",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to specific HTML fixture file to audit",
    )
    parser.add_argument(
        "--fg",
        help="Foreground hex color for direct contrast analysis (e.g. #ffffff)",
    )
    parser.add_argument(
        "--bg",
        help="Background hex color for direct contrast analysis (e.g. #0b57d0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report audit findings without writing any files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root override path",
    )
    args = parser.parse_args(argv)

    # Direct color pair contrast check
    if args.fg and args.bg:
        try:
            fg_rgb = parse_hex(args.fg)
            bg_rgb = parse_hex(args.bg)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        matrix = compute_contrast_matrix(fg_rgb, bg_rgb)
        if args.json:
            print(json_dump(matrix), end="")
        else:
            print(f"WCAG Contrast: {matrix['wcag_contrast_ratio']}:1")
            print(f"  AA Normal Pass:  {matrix['wcag_aa_normal_pass']}")
            print(f"  AAA Normal Pass: {matrix['wcag_aaa_normal_pass']}")
            print(f"APCA Score: {matrix['apca']['score']} ({matrix['apca']['rating']})")
            print(f"  {matrix['apca']['description']}")
            print("Color Blindness Simulation:")
            for cond, res in matrix["color_blindness_simulation"].items():
                print(f"  {cond:14} ratio={res['contrast_ratio']:5.2f}:1  apca={res['apca_score']:7.2f}  AA={res['wcag_aa_pass']}")
        return 0

    root = args.repo_root.resolve() if args.repo_root else repo_root()
    fail_on = {part.strip() for part in args.fail_on.split(",") if part.strip()}
    level = args.level.upper()

    if args.file:
        file_path = args.file.resolve()
        if not file_path.is_file():
            print(f"error: file not found {file_path}", file=sys.stderr)
            return 2
        html = file_path.read_text(encoding="utf-8")
        findings = audit_html(html, file_path.name, level=level)
        gated = [f for f in findings if f["id"] in fail_on]
        payload = {
            "ok": not gated,
            "fixture": file_path.name,
            "level": level,
            "finding_count": len(findings),
            "gated_count": len(gated),
            "findings": findings,
        }
    else:
        payload = run(root=root, engine=args.engine, fail_on=fail_on, level=level)

    if args.json:
        print(json_dump(payload), end="")
    else:
        status = "OK" if payload["ok"] else "FAIL"
        print(
            f"{status} a11y level={level} "
            f"findings={payload['finding_count']} gated={payload['gated_count']}"
        )
        for item in payload["findings"]:
            print(f"  {item['impact']:10} {item['id']:20} {item['fixture']}: {item['help']}")
        if args.dry_run:
            print("dry-run: no files written")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
