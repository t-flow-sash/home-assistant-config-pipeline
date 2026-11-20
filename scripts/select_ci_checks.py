#!/usr/bin/env python3
"""Select focused user contract tests and flag security-sensitive diffs."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import NamedTuple, Sequence

class CheckPlan(NamedTuple):
    tests: tuple[str, ...]
    strict_security: bool

SECURITY_PATHS = (".github/workflows/", "deploy/", "scripts/security_check.py", "scripts/select_ci_checks.py", ".gitignore")
PIPELINE_TESTS = {
    "tests/test_release_safety.py",
    "tests/test_security_check.py",
    "tests/test_select_ci_checks.py",
    "tests/test_validate_ha_yaml.py",
}
SECURITY_TERMS = re.compile(r"(?i)\b(?:shell_command|command_line|rest_command|webhook|password|passwd|token|secret|api[_-]?key|private[_-]?key|alarm|lock|http|auth|proxy|trusted_networks|trusted_users|trusted_proxies|use_x_forwarded_for)\b")
ENTITY = re.compile(r"\b[a-z][a-z0-9_]*\.[a-z0-9_]+\b")
ID = re.compile(r"^\s*(?:[-+]\s*)?(?:id|unique_id|entity_id|alias):\s*[\"']?([^\s#\"']+)", re.M)
DIFF_FILE = re.compile(r"^\+\+\+ b/(.+)$")
DIFF_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

def is_ha_config(path: str) -> bool:
    return path in {"configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml"} or (path.startswith(("packages/", "templates/", "blueprints/", "dashboards/", "ui-")) and path.endswith((".yaml", ".yml")))

def changed_tokens(diff: str) -> set[str]:
    text = "\n".join(line for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))
    return set(ENTITY.findall(text)) | {value for value in ID.findall(text) if len(value) >= 4}

def context_text(root: Path, changed: Sequence[str], diff: str) -> str:
    config = {p for p in changed if is_ha_config(p)}
    touched: dict[str, set[int]] = {}
    current: str | None = None
    for line in diff.splitlines():
        match = DIFF_FILE.match(line)
        if match:
            current = match.group(1)
            continue
        hunk = DIFF_HUNK.match(line)
        if hunk and current in config:
            start, count = int(hunk.group(1)), int(hunk.group(2) or "1")
            touched.setdefault(current, set()).update(range(max(1, start), max(1, start) + max(1, count)))
    blocks: list[str] = []
    for name, positions in touched.items():
        path = root / name
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for position in positions:
            if not lines:
                continue
            index = min(max(position - 1, 0), len(lines) - 1)
            start = index
            while start > 0 and (not lines[start].strip() or lines[start][0].isspace() or lines[start].lstrip().startswith("#")):
                start -= 1
            end = start + 1
            while end < len(lines) and (not lines[end].strip() or lines[end][0].isspace() or lines[end].lstrip().startswith("#")):
                end += 1
            blocks.append("\n".join(lines[start:end]))
    return "\n".join(blocks)

def build_plan(root: Path, changed: Sequence[str], diff: str) -> CheckPlan:
    normalized = tuple(dict.fromkeys(p.strip() for p in changed if p.strip()))
    tests = {
        p
        for p in normalized
        if p.startswith("tests/test_") and p.endswith(".py") and p not in PIPELINE_TESTS
    }
    context = context_text(root, normalized, diff)
    tokens = changed_tokens(diff) | set(ENTITY.findall(context)) | {v for v in ID.findall(context) if len(v) >= 4}
    if tokens and any(is_ha_config(p) for p in normalized):
        for test in sorted((root / "tests").glob("test_*.py")):
            relative = test.relative_to(root).as_posix()
            if relative in PIPELINE_TESTS:
                continue
            source = test.read_text(encoding="utf-8")
            if any(token in source for token in tokens):
                tests.add(relative)
    strict = any(path == prefix or path.startswith(prefix) for path in normalized for prefix in SECURITY_PATHS) or bool(SECURITY_TERMS.search(f"{diff}\n{context}"))
    return CheckPlan(tuple(sorted(tests)), strict)

def git_output(args: list[str], root: Path) -> str:
    return subprocess.check_output(args, cwd=root, text=True)

def quiet_git_output(args: list[str], root: Path) -> str:
    return subprocess.check_output(args, cwd=root, text=True, stderr=subprocess.DEVNULL)

def plan_from_git(root: Path, base: str, head: str) -> CheckPlan:
    try:
        merge_base = quiet_git_output(["git", "merge-base", base, head], root).strip()
    except subprocess.CalledProcessError:
        try:
            merge_base = quiet_git_output(["git", "rev-parse", f"{head}^"], root).strip()
        except subprocess.CalledProcessError:
            merge_base = git_output(["git", "hash-object", "-t", "tree", "/dev/null"], root).strip()
    changed = git_output(["git", "diff", "--name-only", merge_base, head], root).splitlines()
    diff = git_output(["git", "diff", "--unified=0", merge_base, head], root)
    return build_plan(root, changed, diff)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    plan = plan_from_git(root, args.base, args.head)
    payload = {"tests": list(plan.tests), "strict_security": plan.strict_security}
    print(json.dumps(payload, indent=2))
    output = args.github_output or (Path(os.environ["GITHUB_OUTPUT"]) if os.getenv("GITHUB_OUTPUT") else None)
    if output:
        with output.open("a", encoding="utf-8") as handle:
            handle.write(f"has_tests={'true' if plan.tests else 'false'}\n")
            handle.write(f"tests_json={json.dumps(plan.tests, separators=(',', ':'))}\n")
            handle.write(f"strict_security={'true' if plan.strict_security else 'false'}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
