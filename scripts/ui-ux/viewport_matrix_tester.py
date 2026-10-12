"""Verify responsive breakpoint coverage across mobile, tablet, desktop, and 4K viewports against CSS layout definitions.

tags: [ui-ux, responsive, breakpoints, layout]
routing_hints: [viewport, media-queries, reflow, overflow, touch-target, 4k]

Inspects CSS layout rules and HTML component fixtures across five standard viewports:
- Mobile: 320px (WCAG 1.4.10 Reflow threshold)
- Tablet: 768px (iPad portrait / medium breakpoint)
- Desktop: 1024px (Standard landscape desktop breakpoint)
- Desktop Large: 1440px (High-resolution desktop breakpoint)
- 4K Ultra-wide: 3840px (UHD / ultra-wide containment breakpoint)

Detects media query coverage, container queries, fixed-width overflow hazards,
target-size compliance, reflow characteristics, and ultra-wide containment.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _synth import (
    json_dump,
    layout_boxes,
    list_component_html,
    parse_fixture,
    repo_root,
)

STANDARD_VIEWPORTS = (320, 768, 1024, 1440, 3840)

VIEWPORT_PROFILES: dict[int, dict[str, Any]] = {
    320: {
        "name": "mobile",
        "category": "mobile",
        "description": "Mobile portrait / WCAG 1.4.10 320px reflow standard",
        "touch_mandatory": True,
        "max_recommended_columns": 1,
    },
    768: {
        "name": "tablet",
        "category": "tablet",
        "description": "Tablet portrait / iPad standard breakpoint",
        "touch_mandatory": True,
        "max_recommended_columns": 2,
    },
    1024: {
        "name": "desktop_sm",
        "category": "desktop",
        "description": "Compact desktop / tablet landscape breakpoint",
        "touch_mandatory": False,
        "max_recommended_columns": 3,
    },
    1440: {
        "name": "desktop_lg",
        "category": "desktop",
        "description": "Standard high-resolution desktop breakpoint",
        "touch_mandatory": False,
        "max_recommended_columns": 4,
    },
    3840: {
        "name": "4k",
        "category": "ultra_wide",
        "description": "4K UHD / ultra-wide display breakpoint",
        "touch_mandatory": False,
        "max_recommended_columns": 6,
    },
}

MEDIA_QUERY_RE = re.compile(r"@media\s+([^{]+)\{", re.IGNORECASE)
CONTAINER_QUERY_RE = re.compile(r"@container\s+([^{]+)\{", re.IGNORECASE)
MIN_WIDTH_RE = re.compile(r"\(\s*min-width\s*:\s*(\d+(?:\.\d+)?)(px|em|rem)\s*\)", re.IGNORECASE)
MAX_WIDTH_RE = re.compile(r"\(\s*max-width\s*:\s*(\d+(?:\.\d+)?)(px|em|rem)\s*\)", re.IGNORECASE)
FIXED_WIDTH_RE = re.compile(r"(?<![a-zA-Z0-9_-])(?:width)\s*:\s*(\d+)px", re.IGNORECASE)
MAX_WIDTH_PROP_RE = re.compile(r"(?<![a-zA-Z0-9_-])(?:max-width)\s*:\s*([^;]+);", re.IGNORECASE)
CLAMP_RE = re.compile(r"\bclamp\s*\(", re.IGNORECASE)


def parse_viewport_list(raw: str | None) -> tuple[int, ...]:
    """Parse comma-separated viewport width integers into a sorted tuple."""
    if not raw:
        return STANDARD_VIEWPORTS
    values = tuple(sorted({int(part.strip()) for part in raw.split(",") if part.strip()}))
    if not values:
        raise ValueError("viewports must be a comma-separated list of positive integers")
    if any(v <= 0 for v in values):
        raise ValueError("viewport widths must be strictly positive")
    return values


def _to_pixels(val_str: str, unit: str) -> float:
    """Convert a numeric string with px, em, or rem units to CSS pixels (1rem/em = 16px)."""
    val = float(val_str)
    if unit.lower() in ("em", "rem"):
        return val * 16.0
    return val


def extract_media_queries(css: str) -> list[dict[str, Any]]:
    """Extract and parse all @media queries from CSS text into structured bounds."""
    queries: list[dict[str, Any]] = []
    for match in MEDIA_QUERY_RE.finditer(css):
        raw_query = match.group(1).strip()
        min_w: float | None = None
        max_w: float | None = None
        for m in MIN_WIDTH_RE.finditer(raw_query):
            min_w = _to_pixels(m.group(1), m.group(2))
        for m in MAX_WIDTH_RE.finditer(raw_query):
            max_w = _to_pixels(m.group(1), m.group(2))
        queries.append({
            "raw": raw_query,
            "min_width": min_w,
            "max_width": max_w,
        })
    return queries


def extract_container_queries(css: str) -> list[dict[str, Any]]:
    """Extract and parse all @container queries from CSS text."""
    queries: list[dict[str, Any]] = []
    for match in CONTAINER_QUERY_RE.finditer(css):
        raw_query = match.group(1).strip()
        queries.append({"raw": raw_query})
    return queries


def check_query_matches(viewport: int, query: dict[str, Any]) -> bool:
    """Determine whether a given viewport width satisfies a media query's min/max bounds."""
    min_w = query.get("min_width")
    max_w = query.get("max_width")
    if min_w is not None and viewport < min_w:
        return False
    if max_w is not None and viewport > max_w:
        return False
    return True


def strip_css_comments(css: str) -> str:
    """Strip /* ... */ comments from CSS text."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def remove_desktop_media_queries(css: str) -> str:
    """Remove desktop media query blocks (@media with min-width >= 1024px) from CSS text."""
    pos = 0
    result: list[str] = []
    media_re = re.compile(r"@media\s+([^{]+)\{", re.IGNORECASE)

    while pos < len(css):
        m = media_re.search(css, pos)
        if not m:
            result.append(css[pos:])
            break

        # Append text up to @media
        result.append(css[pos:m.start()])

        raw_query = m.group(1).strip()
        min_w: float | None = None
        for wm in MIN_WIDTH_RE.finditer(raw_query):
            min_w = _to_pixels(wm.group(1), wm.group(2))

        # Find matching closing brace for this @media block
        brace_count = 1
        i = m.end()  # right after opening '{'
        while i < len(css) and brace_count > 0:
            if css[i] == "{":
                brace_count += 1
            elif css[i] == "}":
                brace_count -= 1
            i += 1

        # If min-width is >= 1024px, skip the desktop block from hazard evaluation
        if min_w is not None and min_w >= 1024:
            pass
        else:
            result.append(css[m.start():i])

        pos = i

    return "".join(result)


def analyze_css_breakpoints(
    css: str,
    viewports: tuple[int, ...] = STANDARD_VIEWPORTS,
) -> dict[str, Any]:
    """Analyze CSS rules against standard viewport matrix for coverage and hazards."""
    clean_css = strip_css_comments(css)
    media_queries = extract_media_queries(clean_css)
    container_queries = extract_container_queries(clean_css)

    coverage: dict[str, Any] = {}
    for vp in viewports:
        profile = VIEWPORT_PROFILES.get(vp, {"name": f"vp_{vp}", "category": "custom"})
        matching = [q["raw"] for q in media_queries if check_query_matches(vp, q)]
        coverage[str(vp)] = {
            "viewport": vp,
            "name": profile.get("name"),
            "category": profile.get("category"),
            "matching_queries_count": len(matching),
            "matching_queries": matching,
            "has_breakpoint_match": len(matching) > 0,
        }

    # Detect fixed-width overflow hazards (fixed width in px > 320), ignoring desktop media queries (min-width >= 1024px)
    mobile_css = remove_desktop_media_queries(clean_css)
    fixed_widths = [int(m.group(1)) for m in FIXED_WIDTH_RE.finditer(mobile_css)]
    hazards = [
        {"fixed_width": w, "hazard": f"Fixed width {w}px exceeds mobile 320px viewport"}
        for w in fixed_widths
        if w > 320
    ]

    # Detect 4K containment: presence of max-width rules to bound line length
    has_max_width = bool(MAX_WIDTH_PROP_RE.search(clean_css))
    has_fluid_clamp = bool(CLAMP_RE.search(clean_css))

    return {
        "media_query_count": len(media_queries),
        "container_query_count": len(container_queries),
        "media_queries": media_queries,
        "container_queries": container_queries,
        "viewport_coverage": coverage,
        "fixed_width_hazards": hazards,
        "has_4k_containment": has_max_width,
        "has_fluid_scaling": has_fluid_clamp,
    }


def audit_component_layout(
    html: str,
    fixture_name: str,
    viewports: tuple[int, ...] = STANDARD_VIEWPORTS,
    min_target: int = 24,
) -> list[dict[str, Any]]:
    """Test component HTML layout against each viewport in the matrix."""
    parsed = parse_fixture(html)
    issues: list[dict[str, Any]] = []

    for vp in viewports:
        laid = layout_boxes(parsed.boxes, vp)
        for box in laid:
            # Check horizontal overflow
            if box.x + box.w > vp:
                issues.append({
                    "id": "horizontal-overflow",
                    "fixture": fixture_name,
                    "viewport": vp,
                    "role": box.role,
                    "box_x": box.x,
                    "box_w": box.w,
                    "x2": box.x + box.w,
                    "message": f"Element {box.role} ({box.w}px) overflows {vp}px viewport by {(box.x + box.w) - vp}px",
                })
            # Check touch target size on interactive controls
            if box.role in {"button", "textbox", "input", "select"} and (
                box.w < min_target or box.h < min_target
            ):
                issues.append({
                    "id": "target-size",
                    "fixture": fixture_name,
                    "viewport": vp,
                    "role": box.role,
                    "size": [box.w, box.h],
                    "min_required": min_target,
                    "message": f"Touch target {box.role} ({box.w}x{box.h}px) below WCAG 2.5.8 {min_target}px",
                })
    return issues


# Provide alias for callers, but instruct pytest not to collect it as a test
test_component_layout = audit_component_layout
test_component_layout.__test__ = False  # type: ignore[attr-defined]


def run_viewport_matrix_audit(
    root: Path | None = None,
    viewports: tuple[int, ...] = STANDARD_VIEWPORTS,
    css_paths: list[Path] | None = None,
    html_paths: list[Path] | None = None,
    min_target: int = 24,
) -> dict[str, Any]:
    """Execute complete viewport matrix audit across component fixtures and CSS files."""
    base_root = (root or repo_root()).resolve()
    components = html_paths if html_paths is not None else list_component_html(base_root)

    layout_issues: list[dict[str, Any]] = []
    for comp in components:
        content = comp.read_text(encoding="utf-8")
        issues = audit_component_layout(content, comp.name, viewports, min_target)
        layout_issues.extend(issues)

    css_audits: list[dict[str, Any]] = []
    if css_paths:
        for p in css_paths:
            css_text = p.read_text(encoding="utf-8")
            audit = analyze_css_breakpoints(css_text, viewports)
            audit["file"] = p.as_posix()
            css_audits.append(audit)

    return {
        "ok": len(layout_issues) == 0,
        "viewports": list(viewports),
        "component_count": len(components),
        "issue_count": len(layout_issues),
        "issues": layout_issues,
        "css_audits": css_audits,
    }


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and run responsive breakpoint matrix verification."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--viewports",
        help="Comma-separated viewport widths (default 320,768,1024,1440,3840)",
    )
    parser.add_argument(
        "--css",
        type=Path,
        help="Path to CSS file to analyze for breakpoint coverage",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Path to specific HTML fixture to test against viewport matrix",
    )
    parser.add_argument(
        "--min-target",
        type=int,
        default=24,
        help="Minimum touch target size in CSS pixels (default 24 per WCAG 2.5.8)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute verification without writing files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root override path",
    )
    args = parser.parse_args(argv)

    try:
        viewports = parse_viewport_list(args.viewports)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    root = args.repo_root.resolve() if args.repo_root else repo_root()

    # CSS single-file analysis
    if args.css and not args.html:
        css_file = args.css.resolve()
        if not css_file.is_file():
            print(f"error: CSS file not found {css_file}", file=sys.stderr)
            return 2
        css_text = css_file.read_text(encoding="utf-8")
        analysis = analyze_css_breakpoints(css_text, viewports)
        analysis["file"] = css_file.as_posix()
        if args.json:
            print(json_dump(analysis), end="")
        else:
            print(f"CSS Breakpoint Analysis: {css_file.name}")
            print(f"  Media queries: {analysis['media_query_count']}")
            print(f"  4K containment: {analysis['has_4k_containment']}")
            print(f"  Fixed width hazards: {len(analysis['fixed_width_hazards'])}")
            for vp, cov in analysis["viewport_coverage"].items():
                print(f"  {vp:>5}px ({cov['name']:12}): {cov['matching_queries_count']} matching queries")
        return 0

    # HTML single-file analysis
    if args.html:
        html_file = args.html.resolve()
        if not html_file.is_file():
            print(f"error: HTML file not found {html_file}", file=sys.stderr)
            return 2
        html_text = html_file.read_text(encoding="utf-8")
        issues = test_component_layout(html_text, html_file.name, viewports, args.min_target)
        payload = {
            "ok": len(issues) == 0,
            "fixture": html_file.name,
            "viewports": list(viewports),
            "issue_count": len(issues),
            "issues": issues,
        }
        if args.json:
            print(json_dump(payload), end="")
        else:
            status = "OK" if payload["ok"] else "FAIL"
            print(f"{status} layout fixture={html_file.name} issues={len(issues)}")
            for item in issues:
                print(f"  {item['id']:20} {item['viewport']}w: {item['message']}")
        return 0 if payload["ok"] else 1

    # Full audit
    payload = run_viewport_matrix_audit(root=root, viewports=viewports, min_target=args.min_target)
    if args.json:
        print(json_dump(payload), end="")
    else:
        status = "OK" if payload["ok"] else "FAIL"
        print(
            f"{status} viewport matrix viewports={list(viewports)} "
            f"components={payload['component_count']} issues={payload['issue_count']}"
        )
        for item in payload["issues"]:
            print(f"  {item['id']:20} {item['fixture']:28} {item['viewport']}w: {item['message']}")
        if args.dry_run:
            print("dry-run: no files written")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
