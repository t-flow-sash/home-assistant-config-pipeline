from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("selector", ROOT / "scripts/select_ci_checks.py")
assert spec and spec.loader
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)

class SelectorTests(unittest.TestCase):
    def test_changed_test_runs_directly(self):
        plan = selector.build_plan(ROOT, ["tests/test_user_contract.py"], "")
        self.assertEqual(plan.tests, ("tests/test_user_contract.py",))

    def test_changed_pipeline_test_is_not_selected_twice(self):
        plan = selector.build_plan(ROOT, ["tests/test_security_check.py"], "")
        self.assertEqual(plan.tests, ())

    def test_matching_stable_id_selects_user_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "tests").mkdir()
            (root / "tests/test_user_contract.py").write_text("# automation_demo_anchor\n", encoding="utf-8")
            plan = selector.build_plan(root, ["automations.yaml"], "+ id: automation_demo_anchor\n")
            self.assertEqual(plan.tests, ("tests/test_user_contract.py",))

    def test_unmatched_config_does_not_run_all_tests(self):
        plan = selector.build_plan(ROOT, ["automations.yaml"], "+ id: unrelated_demo_anchor\n")
        self.assertEqual(plan.tests, ())

    def test_http_change_is_security_sensitive(self):
        plan = selector.build_plan(ROOT, ["configuration.yaml"], "+ http:\n")
        self.assertTrue(plan.strict_security)

    def test_workflow_is_security_sensitive(self):
        plan = selector.build_plan(ROOT, [".github/workflows/validate.yml"], "")
        self.assertTrue(plan.strict_security)

    def test_script_change_uses_always_on_pipeline_tests(self):
        plan = selector.build_plan(ROOT, ["scripts/validate_ha_yaml.py"], "")
        self.assertEqual(plan.tests, ())

    def test_selector_change_enables_strict_security(self):
        plan = selector.build_plan(ROOT, ["scripts/select_ci_checks.py"], "")
        self.assertTrue(plan.strict_security)

if __name__ == "__main__": unittest.main()
