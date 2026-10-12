import sys
import unittest
from pathlib import Path

# Add validation script dir to sys.path to import it
validation_dir = Path(__file__).resolve().parents[1] / "validation"
sys.path.insert(0, str(validation_dir))

import validate_ui_ux_router


class TestValidateUiUxRouter(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parents[1] / "validation" / "fixtures"
        self.registry_data = validate_ui_ux_router.load_json(validate_ui_ux_router.REGISTRY_PATH)
        self.validated_registry = validate_ui_ux_router.validate_registry(self.registry_data)
        
    def test_valid_cases(self):
        manifest_path = self.fixtures_dir / "ui-cases.json"
        manifest_data = validate_ui_ux_router.load_json(manifest_path)
        cases = manifest_data.get("cases", [])
        self.assertTrue(len(cases) > 0, "No valid cases found")
        
        for c in cases:
            errors = validate_ui_ux_router.validate_case(
                c, 
                self.validated_registry["representations_by_id"],
                self.validated_registry["medium_aliases"]
            )
            self.assertEqual(len(errors), 0, f"Expected valid case, got errors: {errors}")
            
    def test_failing_cases(self):
        manifest_path = self.fixtures_dir / "failing-ui-cases.json"
        manifest_data = validate_ui_ux_router.load_json(manifest_path)
        cases = manifest_data.get("cases", [])
        self.assertTrue(len(cases) > 0, "No failing cases found")
        
        for c in cases:
            errors = validate_ui_ux_router.validate_case(
                c, 
                self.validated_registry["representations_by_id"],
                self.validated_registry["medium_aliases"]
            )
            self.assertTrue(len(errors) > 0, "Expected errors for failing case")
            error_str = " ".join(errors)
            self.assertIn("min_touch_target_px must be at least 24px", error_str)
            self.assertIn("min_text_contrast_ratio must be at least 3.0:1", error_str)
            self.assertIn("missing text", error_str)
            self.assertIn("invalid hardness", error_str)
            self.assertIn("Exactly one primary representation required", error_str)
            self.assertIn("Unknown representation route", error_str)
            self.assertIn("reviewer must be 'accessibility-conformance-auditor'", error_str)
            self.assertIn("violates 24px minimum", error_str)
            self.assertIn("violates minimum threshold", error_str)
            self.assertIn("unresolved WCAG violations", error_str)

if __name__ == '__main__':
    unittest.main()
