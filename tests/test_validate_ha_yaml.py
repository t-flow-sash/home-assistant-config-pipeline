from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_ha_yaml

class ValidateYamlTests(unittest.TestCase):
    def test_empty_template_has_no_config(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(validate_ha_yaml.ha_yaml_files(Path(directory)), [])

    def test_common_tags_and_include_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "part.yaml").write_text("value: !secret example_value\ninput: !input target\n", encoding="utf-8")
            (root / "configuration.yaml").write_text("example: !include part.yaml\n", encoding="utf-8")
            loaded = validate_ha_yaml._load(root / "configuration.yaml")
            self.assertEqual(loaded["example"]["value"], "!secret example_value")

    def test_missing_include_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "configuration.yaml"
            path.write_text("example: !include missing.yaml\n", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                validate_ha_yaml._load(path)

    def test_include_cycle_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "configuration.yaml"
            path.write_text("example: !include configuration.yaml\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_ha_yaml._load(path)

if __name__ == "__main__": unittest.main()
