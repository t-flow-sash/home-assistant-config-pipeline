from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("security", ROOT / "scripts/security_check.py")
assert spec and spec.loader
security = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security)

class SecurityTests(unittest.TestCase):
    def scan_files(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for name, text in files.items():
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8"); paths.append(path)
            with mock.patch.object(security, "candidate_files", return_value=paths):
                return security.scan(root)

    def test_secret_reference_is_allowed(self):
        self.assertEqual(self.scan_files({"configuration.yaml": "example_token: !secret example_token\n"}), [])

    def test_literal_secret_is_rejected(self):
        findings = self.scan_files({"configuration.yaml": "example_password: definitely-not-a-reference\n"})
        self.assertTrue(any("literal secret" in item for item in findings))

    def test_runtime_state_is_rejected(self):
        findings = self.scan_files({".storage/core.config": "{}\n"})
        self.assertTrue(any("runtime/private" in item for item in findings))

    def test_database_is_rejected(self):
        findings = self.scan_files({"home-assistant.db": "not-a-real-database\n"})
        self.assertTrue(any("sensitive file" in item for item in findings))

if __name__ == "__main__": unittest.main()
