"""Headless visual regression against synthetic UI fixtures.

tags: [ui-ux, visual-regression, playwright]
routing_hints: [screenshot, golden, pixel-diff, breakpoints]

Default engine is a deterministic stdlib raster so goldens stay OS-stable.
Pass --engine playwright when Chromium is installed in the same environment
that owns the committed baselines.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _synth import (  # noqa: E402
    CANVAS_HEIGHT,
    PIXEL_THRESHOLD,
    VIEWPORTS,
    baseline_dir,
    baseline_name,
    decode_png_rgb,
    diff_pixels,
    encode_png,
    json_dump,
    list_component_html,
    rasterize,
    repo_root,
)

ENGINES = ("synthetic", "playwright")


def _parse_viewports(raw: str | None) -> tuple[int, ...]:
    if not raw:
        return VIEWPORTS
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("viewports must be a comma-separated list of integers")
    return values


def capture_synthetic(html: str, viewport: int) -> bytes:
    rgb = rasterize(html, viewport)
    return encode_png(viewport, CANVAS_HEIGHT, rgb)


def capture_playwright(html_path: Path, viewport: int) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError(
            "Playwright is not installed. Use --engine synthetic or pip install playwright"
        ) from exc
    html = html_path.resolve().as_uri()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": viewport, "height": CANVAS_HEIGHT})
        page.emulate_media(reduced_motion="reduce")
        page.goto(html)
        page.add_style_tag(
            content="*{animation-duration:0s!important;transition-duration:0s!important}"
        )
        png = page.screenshot(type="png", animations="disabled")
        browser.close()
    return png


def layout_issues(html: str, viewport: int) -> list[dict[str, object]]:
    from _synth import MIN_TARGET_PX, layout_boxes, parse_fixture

    parsed = parse_fixture(html)
    issues: list[dict[str, object]] = []
    for box in layout_boxes(parsed.boxes, viewport):
        if box.role in {"button", "textbox", "input"} and (
            box.w < MIN_TARGET_PX or box.h < MIN_TARGET_PX
        ):
            issues.append(
                {
                    "id": "target-size",
                    "viewport": viewport,
                    "role": box.role,
                    "size": [box.w, box.h],
                    "text": box.text,
                }
            )
        if box.x + box.w > viewport:
            issues.append(
                {
                    "id": "horizontal-overflow",
                    "viewport": viewport,
                    "role": box.role,
                    "x2": box.x + box.w,
                }
            )
    return issues


def run(
    *,
    root: Path,
    engine: str,
    viewports: tuple[int, ...],
    update: bool,
    check_layout: bool,
    dry_run: bool,
) -> dict[str, object]:
    html_files = list_component_html(root)
    gold_dir = baseline_dir(root)
    results: list[dict[str, object]] = []
    mismatches = 0
    layout_fail = 0
    for html_path in html_files:
        html = html_path.read_text(encoding="utf-8")
        for viewport in viewports:
            name = baseline_name(html_path, viewport)
            gold_path = gold_dir / name
            if engine == "playwright":
                png = capture_playwright(html_path, viewport)
            else:
                png = capture_synthetic(html, viewport)
            row: dict[str, object] = {
                "fixture": html_path.name,
                "viewport": viewport,
                "baseline": gold_path.relative_to(root).as_posix(),
                "engine": engine,
            }
            if check_layout:
                issues = layout_issues(html, viewport)
                row["layout_issues"] = issues
                layout_fail += len(issues)
            if update and not dry_run:
                gold_dir.mkdir(parents=True, exist_ok=True)
                gold_path.write_bytes(png)
                row["status"] = "updated"
            elif dry_run and not gold_path.is_file():
                row["status"] = "missing-baseline"
                mismatches += 1
            elif not gold_path.is_file():
                row["status"] = "missing-baseline"
                mismatches += 1
            else:
                _, _, left = decode_png_rgb(gold_path.read_bytes())
                _w, _h, right = decode_png_rgb(png)
                if engine == "synthetic":
                    pixel_miss = diff_pixels(left, right, threshold=PIXEL_THRESHOLD)
                else:
                    # Playwright buffers differ by decoder; compare file digest via pixels when sizes match.
                    pixel_miss = 0 if left == right else diff_pixels(left, right)
                row["diff_pixels"] = pixel_miss
                row["status"] = "pass" if pixel_miss == 0 else "fail"
                if pixel_miss:
                    mismatches += 1
            results.append(row)
    payload = {
        "ok": mismatches == 0 and layout_fail == 0,
        "engine": engine,
        "viewports": list(viewports),
        "threshold": PIXEL_THRESHOLD,
        "mismatches": mismatches,
        "layout_issue_count": layout_fail,
        "results": results,
    }
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=ENGINES, default="synthetic")
    parser.add_argument(
        "--viewports",
        help="Comma-separated CSS widths (default 375,768,1280,1920)",
    )
    parser.add_argument(
        "--update-baselines",
        action="store_true",
        help="Write golden PNGs from the current engine",
    )
    parser.add_argument(
        "--check-layout",
        action="store_true",
        help="Also flag overflow and sub-24px targets (responsive-breakpoint-verify)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve() if args.repo_root else repo_root()
    try:
        viewports = _parse_viewports(args.viewports)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    payload = run(
        root=root,
        engine=args.engine,
        viewports=viewports,
        update=args.update_baselines,
        check_layout=args.check_layout,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json_dump(payload), end="")
    else:
        print(
            f"{'OK' if payload['ok'] else 'FAIL'} visual regression "
            f"engine={payload['engine']} mismatches={payload['mismatches']} "
            f"layout_issues={payload['layout_issue_count']}"
        )
        for row in payload["results"]:
            extra = ""
            if row.get("diff_pixels"):
                extra = f" diff_pixels={row['diff_pixels']}"
            print(f"  {row['status']:16} {row['fixture']:28} {row['viewport']}w{extra}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
