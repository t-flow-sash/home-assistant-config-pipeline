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

    def test_desktop_agents_document_safe_delivery_contract(self):
        guide = (ROOT / "docs/desktop-agents.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for requirement in (
            "Claude Desktop",
            "Codex in der ChatGPT-Desktop-App",
            "Nicht mit **Claude Code** verwechseln",
            "Nicht mit der **Codex CLI** verwechseln",
            "`secrets.yaml`",
            "Kein direkter `main`-Push",
            "./scripts/validate.sh --all",
            "GitHub CI",
            "menschliche Prüfung",
            "`workflow_dispatch` auf `main`",
            "kein selbst gehosteter Runner nötig",
            "kontrollierte manuelle lokale Bereitstellung",
            "Eigene CI-Runner und Deployment-Runner bleiben getrennt",
            "keine Home-Assistant-MCP-",
            "danger-full-access",
        ):
            self.assertIn(requirement, guide)

        for requirement in (
            "Pushe niemals direkt nach `main`",
            "Greife niemals auf das Home-Assistant-Verzeichnis `/config`",
            "Starte keinen Deployment-Workflow",
            "menschliche PR-Prüfung",
            "zwei dokumentierte Endpfade",
        ):
            self.assertIn(requirement, agents)

    def test_primary_docs_distinguish_all_three_operating_models(self):
        for relative_path in (
            "README.md",
            "docs/quickstart.md",
            "docs/architecture.md",
            "docs/deployment.md",
            "docs/self-hosted-runner.md",
        ):
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("Desktop-only", content, relative_path)
            self.assertIn("eigene agenten", content.casefold(), relative_path)
            self.assertIn("Hybrid", content, relative_path)

    def test_architecture_compares_agent_ci_deployment_and_runner_need(self):
        architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
        self.assertIn("Eigene Agenten + eigene lokale Runner", architecture)
        self.assertIn("Desktop-only ohne eigene Runner", architecture)
        self.assertIn("Hybrid Desktop-Agent + GitHub Actions", architecture)
        self.assertIn("| Modell | Agent | CI | Deployment | Eigener Runner nötig |", architecture)

    def test_desktop_only_documents_complete_manual_deployment(self):
        guide = (ROOT / "docs/deployment.md").read_text(encoding="utf-8")
        for requirement in (
            "git pull --ff-only origin main",
            "vollständiges Backup",
            "Studio Code Server/File Editor",
            "Samba",
            "SSH",
            "Konfiguration prüfen",
            "betroffenen Bereich neu",
            "Live-Readback",
            "Git-Revert-Pull-Request",
        ):
            self.assertIn(requirement, guide)

    def test_docs_enforce_runner_and_desktop_security_boundaries(self):
        architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
        runner = (ROOT / "docs/self-hosted-runner.md").read_text(encoding="utf-8")
        deployment = (ROOT / "docs/deployment.md").read_text(encoding="utf-8")
        self.assertIn("GitHub-gehosteter Runner greift niemals direkt auf Heimnetz", architecture)
        self.assertIn("CI-Runner und ein lokaler Deployment-Runner", architecture)
        self.assertIn("Desktop-Agent erhält niemals Zugriff auf Live-Mount, Credentials oder Deployment", architecture)
        self.assertIn("Self-hosted Deployment-Runner führt niemals Pull-Request-Code aus", runner)
        for unsafe_generic_writer in ("cp -r ", "rm -r ", "rsync -a "):
            self.assertNotIn(unsafe_generic_writer, deployment)

    def test_primary_docs_link_to_desktop_agent_guide(self):
        for relative_path in (
            "README.md",
            "docs/quickstart.md",
            "docs/architecture.md",
            "docs/deployment.md",
            "docs/troubleshooting.md",
        ):
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("desktop-agents.md", content, relative_path)

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