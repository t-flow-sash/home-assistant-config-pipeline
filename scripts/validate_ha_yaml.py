#!/usr/bin/env python3
"""Parse repository-owned Home Assistant YAML with common HA tags."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = ("configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml")
DIRECTORIES = ("packages", "templates", "blueprints", "dashboards")

class HALoader(yaml.SafeLoader):
    pass

def _scalar_tag(label: str):
    def construct(loader: HALoader, node: yaml.Node) -> str:
        return f"{label} {loader.construct_scalar(node)}"
    return construct

def _load(path: Path, seen: set[Path] | None = None) -> Any:
    seen = set() if seen is None else set(seen)
    path = path.resolve()
    if path in seen:
        raise ValueError(f"include cycle involving {path}")
    if not path.is_file():
        raise FileNotFoundError(f"included file does not exist: {path}")
    seen.add(path)

    class FileLoader(HALoader):
        pass

    def include(loader: FileLoader, node: yaml.Node) -> Any:
        return _load(path.parent / loader.construct_scalar(node), seen)

    def include_dir(loader: FileLoader, node: yaml.Node) -> Any:
        directory = path.parent / loader.construct_scalar(node)
        if not directory.is_dir():
            raise FileNotFoundError(f"included directory does not exist: {directory}")
        items = sorted(p for p in directory.rglob("*") if p.suffix in {".yaml", ".yml"})
        values = [_load(item, seen) for item in items]
        if node.tag in {"!include_dir_list", "!include_dir_merge_list"}:
            if node.tag.endswith("merge_list"):
                merged: list[Any] = []
                for value in values:
                    if not isinstance(value, list):
                        raise ValueError(f"{node.tag} requires list documents in {directory}")
                    merged.extend(value)
                return merged
            return values
        if node.tag == "!include_dir_merge_named":
            merged_dict: dict[str, Any] = {}
            for value in values:
                if not isinstance(value, dict):
                    raise ValueError(f"{node.tag} requires mapping documents in {directory}")
                merged_dict.update(value)
            return merged_dict
        return {item.stem: _load(item, seen) for item in items}

    FileLoader.add_constructor("!secret", _scalar_tag("!secret"))
    FileLoader.add_constructor("!input", _scalar_tag("!input"))
    FileLoader.add_constructor("!include", include)
    for tag in ("!include_dir_merge_named", "!include_dir_list", "!include_dir_named", "!include_dir_merge_list"):
        FileLoader.add_constructor(tag, include_dir)
    with path.open(encoding="utf-8") as handle:
        return yaml.load(handle, Loader=FileLoader)

def ha_yaml_files(root: Path = ROOT) -> list[Path]:
    files = [root / name for name in TOP_LEVEL]
    files.extend(sorted(root.glob("ui-*.yaml")))
    files.extend(sorted(root.glob("ui-*.yml")))
    for name in DIRECTORIES:
        directory = root / name
        if directory.is_dir():
            files.extend(sorted(p for p in directory.rglob("*") if p.suffix in {".yaml", ".yml"}))
    return list(dict.fromkeys(p for p in files if p.is_file()))

def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    files = ha_yaml_files()
    if not files:
        print("No Home Assistant YAML found; this is expected in a fresh template repository.")
        return 0
    failed = False
    for path in files:
        try:
            _load(path)
            print(f"OK {path.relative_to(ROOT)}")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            failed = True
            print(f"ERROR {path.relative_to(ROOT)}: {exc}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
