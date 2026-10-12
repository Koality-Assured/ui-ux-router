"""Tests for ui-ux synthetic visual, a11y, and token gates.

tags: [tests, ui-ux]
routing_hints: [visual-regression, accessibility, design-tokens]

Run: python -m unittest scripts.tests.test_ui_ux -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
_UI = _SCRIPTS / "ui-ux"
for path in (_SCRIPTS, _UI):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from audit_accessibility import audit_html, run as run_a11y  # noqa: E402
from compile_design_tokens import compile_tokens  # noqa: E402
from run_visual_regression import run as run_visual  # noqa: E402
from _synth import repo_root  # noqa: E402


class TestVisualRegression(unittest.TestCase):
    def test_synthetic_compare_is_deterministic(self) -> None:
        root = repo_root()
        first = run_visual(
            root=root,
            engine="synthetic",
            viewports=(375, 1280),
            update=False,
            check_layout=False,
            dry_run=False,
        )
        second = run_visual(
            root=root,
            engine="synthetic",
            viewports=(375, 1280),
            update=False,
            check_layout=False,
            dry_run=False,
        )
        self.assertTrue(first["ok"], first)
        self.assertEqual(first["mismatches"], 0)
        self.assertEqual(second["mismatches"], 0)

    def test_layout_flags_undersized_target(self) -> None:
        payload = run_visual(
            root=repo_root(),
            engine="synthetic",
            viewports=(375,),
            update=False,
            check_layout=True,
            dry_run=False,
        )
        ids = {
            (row["fixture"], issue["id"])
            for row in payload["results"]
            for issue in row.get("layout_issues", [])
        }
        self.assertIn(("button-fail-target.html", "target-size"), ids)


class TestAccessibility(unittest.TestCase):
    def test_planted_contrast_and_trap(self) -> None:
        root = repo_root()
        payload = run_a11y(
            root=root,
            engine="synthetic",
            fail_on={"contrast", "keyboard-trap"},
        )
        ids = {(item["fixture"], item["id"]) for item in payload["findings"]}
        self.assertIn(("button-fail-contrast.html", "contrast"), ids)
        self.assertIn(("modal-fail-trap.html", "keyboard-trap"), ids)
        self.assertFalse(payload["ok"])

    def test_ok_button_has_no_contrast_finding(self) -> None:
        html = (repo_root() / "scripts/ui-ux/fixtures/components/button-ok.html").read_text(
            encoding="utf-8"
        )
        findings = audit_html(html, "button-ok.html")
        self.assertFalse(any(item["id"] == "contrast" for item in findings), findings)

    def test_unlabeled_control_is_flagged(self) -> None:
        html = (
            repo_root() / "scripts/ui-ux/fixtures/components/form-fail-unlabeled.html"
        ).read_text(encoding="utf-8")
        findings = audit_html(html, "form-fail-unlabeled.html")
        self.assertTrue(any(item["id"] == "control-unlabeled" for item in findings), findings)


class TestTokens(unittest.TestCase):
    def test_fixture_tokens_compile(self) -> None:
        raw = json.loads(
            (repo_root() / "scripts/ui-ux/fixtures/tokens/tokens.json").read_text(
                encoding="utf-8"
            )
        )
        payload = compile_tokens(raw)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("--color-action:", payload["css"])
        self.assertGreaterEqual(payload["token_count"], 6)

    def test_mixed_legacy_value_rejected(self) -> None:
        payload = compile_tokens(
            {"color": {"ink": {"$type": "color", "$value": "#111111", "value": "#111111"}}}
        )
        self.assertFalse(payload["ok"])
        self.assertTrue(any("mixed" in err for err in payload["errors"]))


class TestDryRunCli(unittest.TestCase):
    def test_visual_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # dry-run against real goldens; just ensure callable
            payload = run_visual(
                root=repo_root(),
                engine="synthetic",
                viewports=(375,),
                update=True,
                check_layout=False,
                dry_run=True,
            )
            self.assertTrue(payload["results"])
            del tmp


if __name__ == "__main__":
    unittest.main()
