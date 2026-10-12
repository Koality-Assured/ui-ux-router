"""Comprehensive unit tests for UI/UX automation scripts and CLI interfaces.

tags: [tests, ui-ux]
routing_hints: [design-tokens, accessibility, breakpoints, apca]

Tests all functions, edge cases, and CLI invocations for:
- compile_design_tokens.py (CSS, SCSS, Tailwind, TypeScript compilation, DTCG validation)
- audit_accessibility.py (WCAG AA/AAA, APCA score, touch target size, CVD simulation matrices)
- viewport_matrix_tester.py (Breakpoint coverage, 320/768/1024/1440/3840 viewports, overflow, 4K containment)
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
_UI = _SCRIPTS / "ui-ux"
for path in (_SCRIPTS, _UI):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from compile_design_tokens import (  # noqa: E402
    compile_tokens,
    css_name,
    main as tokens_main,
    render_css,
    render_scss,
    render_tailwind,
    render_typescript,
    resolve,
)
from audit_accessibility import (  # noqa: E402
    apca_contrast,
    audit_html,
    compute_contrast_matrix,
    evaluate_apca,
    evaluate_color_blindness,
    evaluate_wcag_contrast,
    main as a11y_main,
    simulate_cvd,
    srgb_to_y,
    verify_touch_target_size,
)
from viewport_matrix_tester import (  # noqa: E402
    STANDARD_VIEWPORTS,
    analyze_css_breakpoints,
    check_query_matches,
    extract_container_queries,
    extract_media_queries,
    main as viewport_main,
    parse_viewport_list,
    run_viewport_matrix_audit,
    test_component_layout,
)
from _synth import repo_root  # noqa: E402


class TestCompileDesignTokens(unittest.TestCase):
    """Unit and CLI tests for compile_design_tokens.py."""

    def setUp(self) -> None:
        self.valid_raw = {
            "color": {
                "$type": "color",
                "brand": {
                    "primary": {
                        "$type": "color",
                        "$value": "#0b57d0",
                        "$description": "Primary brand color",
                    },
                    "surface": {
                        "$type": "color",
                        "$value": "{color.brand.primary}",
                        "$description": "Surface background alias",
                    },
                },
            },
            "spacing": {
                "$type": "dimension",
                "sm": {
                    "$type": "dimension",
                    "$value": "8px",
                },
                "md": {
                    "$type": "dimension",
                    "$value": "16px",
                    "$description": "Medium margin",
                },
            },
        }

    def test_compile_tokens_success(self) -> None:
        payload = compile_tokens(self.valid_raw)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["token_count"], 4)

        # CSS checks
        self.assertIn(":root {", payload["css"])
        self.assertIn("--color-brand-primary: #0b57d0;", payload["css"])
        self.assertIn("--color-brand-surface: #0b57d0;", payload["css"])
        self.assertIn("--spacing-sm: 8px;", payload["css"])

        # SCSS checks
        self.assertIn("$color-brand-primary: #0b57d0;", payload["scss"])
        self.assertIn("$spacing-md: 16px;", payload["scss"])

        # Tailwind checks
        tailwind = json.loads(payload["tailwind"])
        self.assertIn("theme", tailwind)
        self.assertEqual(tailwind["theme"]["extend"]["colors"]["brand.primary"], "#0b57d0")

        # TypeScript checks
        ts = payload["typescript"]
        self.assertIn("export const tokens = {", ts)
        self.assertIn('"color.brand.primary": "#0b57d0"', ts)
        self.assertIn("export type TokenName = keyof typeof tokens;", ts)
        self.assertIn("export type TokenValue = typeof tokens[TokenName];", ts)
        self.assertIn("export const tokenMetadata: Record<TokenName, TokenDefinition> = {", ts)
        self.assertIn("export const tokenTree = {", ts)
        self.assertIn("export type TokenTree = typeof tokenTree;", ts)
        self.assertIn("as const;", ts)

    def test_css_name_formatting(self) -> None:
        self.assertEqual(css_name("color.brand.primary"), "--color-brand-primary")
        self.assertEqual(css_name("font.size.base"), "--font-size-base")

    def test_resolve_missing_alias(self) -> None:
        tokens = {
            "color.bad": {
                "path": "color.bad",
                "type": "color",
                "value": "{color.nonexistent}",
            }
        }
        errors = resolve(tokens)
        self.assertTrue(any("missing" in err for err in errors))

    def test_resolve_multi_hop_aliases(self) -> None:
        raw = {
            "color": {
                "palette": {
                    "blue500": {
                        "$type": "color",
                        "$value": "#3b82f6",
                    }
                },
                "brand": {
                    "primary": {
                        "$type": "color",
                        "$value": "{color.brand.main}",
                    },
                    "main": {
                        "$type": "color",
                        "$value": "{color.palette.blue500}",
                    },
                },
            }
        }
        payload = compile_tokens(raw)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["tokens"]["color.brand.primary"]["resolved"], "#3b82f6")
        self.assertEqual(payload["tokens"]["color.brand.main"]["resolved"], "#3b82f6")
        self.assertEqual(payload["tokens"]["color.palette.blue500"]["resolved"], "#3b82f6")

    def test_resolve_circular_alias_reference(self) -> None:
        tokens = {
            "color.a": {
                "path": "color.a",
                "type": "color",
                "value": "{color.b}",
            },
            "color.b": {
                "path": "color.b",
                "type": "color",
                "value": "{color.a}",
            },
        }
        errors = resolve(tokens)
        self.assertTrue(any("circular" in err for err in errors))

    def test_reject_mixed_legacy_value(self) -> None:
        mixed = {
            "color": {
                "ink": {
                    "$type": "color",
                    "$value": "#111111",
                    "value": "#111111",
                }
            }
        }
        payload = compile_tokens(mixed)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("mixed legacy" in err for err in payload["errors"]))

    def test_reject_legacy_value_without_dtcg(self) -> None:
        legacy = {
            "color": {
                "ink": {
                    "$type": "color",
                    "value": "#111111",
                }
            }
        }
        payload = compile_tokens(legacy)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("legacy value key is not allowed" in err for err in payload["errors"]))

    def test_reject_missing_and_invalid_type(self) -> None:
        missing_type = {
            "color": {
                "test": {
                    "$value": "#123456",
                }
            }
        }
        payload = compile_tokens(missing_type)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("$type missing" in err for err in payload["errors"]))

        invalid_type = {
            "color": {
                "test": {
                    "$type": "unsupported-type-xyz",
                    "$value": "#123456",
                }
            }
        }
        payload = compile_tokens(invalid_type)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("not in fixture subset" in err for err in payload["errors"]))

    def test_cli_out_dir_and_dry_run(self) -> None:
        fixture_path = repo_root() / "scripts/ui-ux/fixtures/tokens/tokens.json"
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "output"

            # Dry run: should NOT write files
            code_dry = tokens_main(["--input", str(fixture_path), "--out-dir", str(out), "--dry-run"])
            self.assertEqual(code_dry, 0)
            self.assertFalse(out.exists())

            # Real run: should write all 4 token output files
            code_run = tokens_main(["--input", str(fixture_path), "--out-dir", str(out), "--json"])
            self.assertEqual(code_run, 0)
            self.assertTrue((out / "tokens.css").is_file())
            self.assertTrue((out / "tokens.scss").is_file())
            self.assertTrue((out / "tailwind.theme.json").is_file())
            self.assertTrue((out / "tokens.ts").is_file())

            # Check tokens.ts content
            ts_content = (out / "tokens.ts").read_text(encoding="utf-8")
            self.assertIn("export const tokens =", ts_content)
            self.assertIn("export const tokenTree =", ts_content)

    def test_cli_missing_input_file(self) -> None:
        code = tokens_main(["--input", "non_existent_file.json"])
        self.assertEqual(code, 2)


class TestAuditAccessibility(unittest.TestCase):
    """Unit and CLI tests for audit_accessibility.py."""

    def test_srgb_to_y(self) -> None:
        y_black = srgb_to_y((0, 0, 0))
        y_white = srgb_to_y((255, 255, 255))
        self.assertAlmostEqual(y_white, 1.0, places=4)
        self.assertGreater(y_white, y_black)
        self.assertGreater(y_black, 0.0)  # APCA soft clip applied for low values

    def test_apca_contrast(self) -> None:
        # Same color produces 0.0
        score_same = apca_contrast((128, 128, 128), (128, 128, 128))
        self.assertEqual(score_same, 0.0)

        # Dark text on light background produces positive score
        score_black_on_white = apca_contrast((0, 0, 0), (255, 255, 255))
        self.assertGreater(score_black_on_white, 100.0)

        # Light text on dark background produces negative score
        score_white_on_dark = apca_contrast((255, 255, 255), (11, 87, 208))
        self.assertLess(score_white_on_dark, -80.0)

    def test_evaluate_apca(self) -> None:
        pref = evaluate_apca(95.0)
        self.assertEqual(pref["rating"], "preferred-body")
        self.assertTrue(pref["accessible_body"])

        body = evaluate_apca(78.0)
        self.assertEqual(body["rating"], "minimum-body")
        self.assertTrue(body["accessible_body"])

        large = evaluate_apca(62.0)
        self.assertEqual(large["rating"], "large-text")
        self.assertFalse(large["accessible_body"])
        self.assertTrue(large["accessible_large"])

        fail = evaluate_apca(15.0)
        self.assertEqual(fail["rating"], "fail")
        self.assertFalse(fail["accessible_body"])

    def test_evaluate_wcag_contrast(self) -> None:
        # AA normal (4.5:1)
        self.assertTrue(evaluate_wcag_contrast(4.5, "AA", is_large_text=False))
        self.assertFalse(evaluate_wcag_contrast(4.4, "AA", is_large_text=False))

        # AA large (3.0:1)
        self.assertTrue(evaluate_wcag_contrast(3.0, "AA", is_large_text=True))
        self.assertFalse(evaluate_wcag_contrast(2.9, "AA", is_large_text=True))

        # AAA normal (7.0:1)
        self.assertTrue(evaluate_wcag_contrast(7.0, "AAA", is_large_text=False))
        self.assertFalse(evaluate_wcag_contrast(6.9, "AAA", is_large_text=False))

        # AAA large (4.5:1)
        self.assertTrue(evaluate_wcag_contrast(4.5, "AAA", is_large_text=True))
        self.assertFalse(evaluate_wcag_contrast(4.4, "AAA", is_large_text=True))

    def test_verify_touch_target_size(self) -> None:
        aa_ok = verify_touch_target_size(24, 24, "AA")
        self.assertTrue(aa_ok["pass"])
        self.assertEqual(aa_ok["min_required"], 24)

        aa_fail = verify_touch_target_size(20, 24, "AA")
        self.assertFalse(aa_fail["pass"])

        aaa_ok = verify_touch_target_size(44, 44, "AAA")
        self.assertTrue(aaa_ok["pass"])
        self.assertEqual(aaa_ok["min_required"], 44)

        aaa_fail = verify_touch_target_size(40, 44, "AAA")
        self.assertFalse(aaa_fail["pass"])

    def test_simulate_cvd_matrices(self) -> None:
        white = (255, 255, 255)
        for condition in ("protanopia", "deuteranopia", "tritanopia", "achromatopsia"):
            sim = simulate_cvd(white, condition)
            # White stays (255, 255, 255) under all CVD transformations
            self.assertEqual(sim, (255, 255, 255))

        # Test unknown deficiency
        with self.assertRaises(ValueError):
            simulate_cvd((100, 100, 100), "unknown-deficiency")

    def test_evaluate_color_blindness(self) -> None:
        fg = (255, 255, 255)
        bg = (11, 87, 208)
        results = evaluate_color_blindness(fg, bg)
        self.assertEqual(set(results.keys()), {"protanopia", "deuteranopia", "tritanopia", "achromatopsia"})
        for cond, res in results.items():
            self.assertIn("contrast_ratio", res)
            self.assertIn("apca_score", res)
            self.assertIn("wcag_aa_pass", res)
            self.assertIn("wcag_aaa_pass", res)

    def test_compute_contrast_matrix(self) -> None:
        matrix = compute_contrast_matrix((255, 255, 255), (11, 87, 208))
        self.assertIn("wcag_contrast_ratio", matrix)
        self.assertIn("wcag_aa_normal_pass", matrix)
        self.assertIn("apca", matrix)
        self.assertIn("color_blindness_simulation", matrix)
        self.assertTrue(matrix["wcag_aa_normal_pass"])

    def test_audit_html_fixtures(self) -> None:
        comp_dir = repo_root() / "scripts/ui-ux/fixtures/components"

        # button-ok.html passes AA
        ok_html = (comp_dir / "button-ok.html").read_text(encoding="utf-8")
        ok_findings = audit_html(ok_html, "button-ok.html", level="AA")
        self.assertEqual(ok_findings, [])

        # button-ok.html flags contrast under AAA (6.39:1 < 7.0:1)
        aaa_findings = audit_html(ok_html, "button-ok.html", level="AAA")
        self.assertTrue(any(f["id"] == "contrast" for f in aaa_findings))

        # button-fail-contrast.html flags contrast
        fail_contrast_html = (comp_dir / "button-fail-contrast.html").read_text(encoding="utf-8")
        findings_contrast = audit_html(fail_contrast_html, "button-fail-contrast.html")
        self.assertTrue(any(f["id"] == "contrast" for f in findings_contrast))

        # button-fail-target.html flags target-size
        fail_target_html = (comp_dir / "button-fail-target.html").read_text(encoding="utf-8")
        findings_target = audit_html(fail_target_html, "button-fail-target.html")
        self.assertTrue(any(f["id"] == "target-size" for f in findings_target))

        # form-fail-unlabeled.html flags control-unlabeled
        fail_unlabeled_html = (comp_dir / "form-fail-unlabeled.html").read_text(encoding="utf-8")
        findings_unlabeled = audit_html(fail_unlabeled_html, "form-fail-unlabeled.html")
        self.assertTrue(any(f["id"] == "control-unlabeled" for f in findings_unlabeled))

        # modal-fail-trap.html flags keyboard-trap
        fail_trap_html = (comp_dir / "modal-fail-trap.html").read_text(encoding="utf-8")
        findings_trap = audit_html(fail_trap_html, "modal-fail-trap.html")
        self.assertTrue(any(f["id"] == "keyboard-trap" for f in findings_trap))

    def test_cli_color_pair_check(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = a11y_main(["--fg", "#ffffff", "--bg", "#0b57d0", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertIn("wcag_contrast_ratio", data)
        self.assertIn("color_blindness_simulation", data)

    def test_cli_single_file_audit(self) -> None:
        comp_path = repo_root() / "scripts/ui-ux/fixtures/components/button-ok.html"
        code = a11y_main(["--file", str(comp_path), "--level", "AA"])
        self.assertEqual(code, 0)

        fail_path = repo_root() / "scripts/ui-ux/fixtures/components/button-fail-contrast.html"
        code_fail = a11y_main(["--file", str(fail_path), "--level", "AA"])
        self.assertEqual(code_fail, 1)

    def test_cli_fg_without_bg_raises_error(self) -> None:
        buf_err = io.StringIO()
        with redirect_stderr(buf_err):
            code = a11y_main(["--fg", "#ffffff"])
        self.assertEqual(code, 2)
        self.assertIn("--bg must be provided", buf_err.getvalue())

        buf_err2 = io.StringIO()
        with redirect_stderr(buf_err2):
            code2 = a11y_main(["--bg", "#000000"])
        self.assertEqual(code2, 2)
        self.assertIn("--fg must be provided", buf_err2.getvalue())


class TestViewportMatrixTester(unittest.TestCase):
    """Unit and CLI tests for viewport_matrix_tester.py."""

    def test_parse_viewport_list(self) -> None:
        # Default standard viewports
        self.assertEqual(parse_viewport_list(None), STANDARD_VIEWPORTS)

        # Custom parsed list
        custom = parse_viewport_list("320, 768, 1440")
        self.assertEqual(custom, (320, 768, 1440))

        # Invalid non-positive
        with self.assertRaises(ValueError):
            parse_viewport_list("0, 1024")

    def test_extract_media_queries(self) -> None:
        css = """
        @media (min-width: 768px) { .nav { display: flex; } }
        @media (min-width: 64em) and (max-width: 90em) { .main { padding: 2rem; } }
        """
        queries = extract_media_queries(css)
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0]["min_width"], 768.0)
        self.assertIsNone(queries[0]["max_width"])
        self.assertEqual(queries[1]["min_width"], 1024.0)  # 64em * 16 = 1024px
        self.assertEqual(queries[1]["max_width"], 1440.0)  # 90em * 16 = 1440px

    def test_extract_container_queries(self) -> None:
        css = "@container (min-width: 400px) { .card { grid-template-columns: 1fr 1fr; } }"
        cq = extract_container_queries(css)
        self.assertEqual(len(cq), 1)
        self.assertIn("min-width: 400px", cq[0]["raw"])

    def test_check_query_matches(self) -> None:
        query = {"min_width": 768.0, "max_width": 1024.0}
        self.assertFalse(check_query_matches(320, query))
        self.assertTrue(check_query_matches(768, query))
        self.assertTrue(check_query_matches(1024, query))
        self.assertFalse(check_query_matches(1440, query))

    def test_analyze_css_breakpoints_hazards_and_4k(self) -> None:
        css = """
        /* Fluid container with 4K max-width constraint */
        .wrapper { width: 100%; max-width: 1440px; margin: 0 auto; }
        /* Fixed width hazard on mobile */
        .banner { width: 600px; }
        @media (min-width: 768px) { .grid { display: grid; } }
        @media (min-width: 1024px) { .grid { grid-template-columns: 1fr 1fr; } }
        """
        analysis = analyze_css_breakpoints(css)
        self.assertEqual(analysis["media_query_count"], 2)
        self.assertTrue(analysis["has_4k_containment"])

        # Fixed width hazard flagged
        hazards = analysis["fixed_width_hazards"]
        self.assertEqual(len(hazards), 1)
        self.assertEqual(hazards[0]["fixed_width"], 600)

        # Coverage across viewports
        cov = analysis["viewport_coverage"]
        self.assertIn("320", cov)
        self.assertIn("768", cov)
        self.assertIn("1024", cov)
        self.assertIn("1440", cov)
        self.assertIn("3840", cov)
        self.assertEqual(cov["320"]["matching_queries_count"], 0)
        self.assertEqual(cov["768"]["matching_queries_count"], 1)
        self.assertEqual(cov["1024"]["matching_queries_count"], 2)

    def test_analyze_css_breakpoints_strips_comments_and_ignores_desktop_media_queries(self) -> None:
        css = """
        /* Commented out rule must not trigger hazard: width: 500px; */
        .mobile-safe { width: 100%; }

        /* Desktop-only media query must be ignored for mobile hazards */
        @media (min-width: 1024px) {
            .desktop-sidebar {
                width: 480px;
            }
        }
        @media screen and (min-width: 1200px) {
            .large-container {
                width: 1100px;
            }
        }
        """
        analysis = analyze_css_breakpoints(css)
        self.assertEqual(len(analysis["fixed_width_hazards"]), 0)
        self.assertEqual(analysis["media_query_count"], 2)

    def test_component_layout_pass_and_overflow(self) -> None:
        # button-ok.html passes across all viewports
        comp_dir = repo_root() / "scripts/ui-ux/fixtures/components"
        ok_html = (comp_dir / "button-ok.html").read_text(encoding="utf-8")
        issues_ok = test_component_layout(ok_html, "button-ok.html")
        self.assertEqual(issues_ok, [])

        # button-fail-target.html has target-size issues across all viewports
        target_html = (comp_dir / "button-fail-target.html").read_text(encoding="utf-8")
        issues_target = test_component_layout(target_html, "button-fail-target.html")
        self.assertEqual(len(issues_target), len(STANDARD_VIEWPORTS))
        self.assertTrue(all(issue["id"] == "target-size" for issue in issues_target))

        # Intentionally wide component overflowing 320px
        overflow_html = """
        <!DOCTYPE html>
        <html lang="en"><body><main>
          <div data-role="button" data-w="400" data-h="48" data-bg="#0b57d0" data-fg="#ffffff">Wide</div>
        </main></body></html>
        """
        issues_overflow = test_component_layout(overflow_html, "overflow.html", viewports=(320, 768))
        # At 320px, 8 + 400 = 408 > 320 -> horizontal overflow
        self.assertTrue(any(i["id"] == "horizontal-overflow" and i["viewport"] == 320 for i in issues_overflow))
        # At 768px, 8 + 400 = 408 <= 768 -> no horizontal overflow
        self.assertFalse(any(i["id"] == "horizontal-overflow" and i["viewport"] == 768 for i in issues_overflow))

    def test_run_viewport_matrix_audit(self) -> None:
        root = repo_root()
        audit = run_viewport_matrix_audit(root=root)
        self.assertEqual(audit["viewports"], list(STANDARD_VIEWPORTS))
        self.assertGreater(audit["component_count"], 0)
        # button-fail-target.html is caught
        self.assertFalse(audit["ok"])
        self.assertGreater(audit["issue_count"], 0)

    def test_cli_execution(self) -> None:
        # CLI single HTML fixture test
        ok_file = repo_root() / "scripts/ui-ux/fixtures/components/button-ok.html"
        code_ok = viewport_main(["--html", str(ok_file), "--json"])
        self.assertEqual(code_ok, 0)

        # CLI failing HTML fixture
        fail_file = repo_root() / "scripts/ui-ux/fixtures/components/button-fail-target.html"
        code_fail = viewport_main(["--html", str(fail_file), "--dry-run"])
        self.assertEqual(code_fail, 1)

        # CLI CSS analysis
        with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False) as tmp:
            tmp.write(".container { max-width: 1200px; } @media (min-width: 768px) {}")
            tmp_path = Path(tmp.name)
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code_css = viewport_main(["--css", str(tmp_path), "--json"])
            self.assertEqual(code_css, 0)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["media_query_count"], 1)
            self.assertTrue(data["has_4k_containment"])
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
