from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseSafetyTests(unittest.TestCase):
    def test_repository_has_no_generic_mutating_deploy_script(self):
        deploy = ROOT / "deploy"
        scripts = list(deploy.glob("*.sh")) if deploy.is_dir() else []
        self.assertEqual(scripts, [])

    def test_manual_github_deployment_documents_safe_contract(self):
        guide = (ROOT / "docs/github-triggered-deployment.md").read_text(encoding="utf-8")
        for requirement in (
            "workflow_dispatch",
            "github.ref == 'refs/heads/main'",
            "Absichtlich kein actions/checkout",
            "origin/main",
            "erfolgreicher **Push-Lauf auf `main`**",
            "exklusives Lock",
            "vollständiges, wiederherstellbares Backup",
            "Rollback → erneutes `check_config`",
            "keinen automatischen Reload oder Restart",
            "Required reviewers",
        ):
            self.assertIn(requirement, guide)

    def test_pipeline_tests_run_exactly_once_without_discovery(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        for module in (
            "tests.test_release_safety",
            "tests.test_security_check",
            "tests.test_select_ci_checks",
            "tests.test_validate_ha_yaml",
        ):
            self.assertEqual(workflow.count(module), 1)
        self.assertNotIn("unittest discover", workflow)

    def test_workflow_uses_json_argv_for_selected_tests(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn('SELECTED_TESTS_JSON: ${{ steps.plan.outputs.tests_json }}', workflow)
        self.assertNotIn("python -m unittest ${{ steps.plan.outputs", workflow)

    def test_strict_security_controls_history_scan(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("if: steps.plan.outputs.strict_security == 'true'", workflow)
        self.assertIn('"$RUNNER_TEMP/gitleaks" git --redact --verbose .', workflow)


if __name__ == "__main__":
    unittest.main()