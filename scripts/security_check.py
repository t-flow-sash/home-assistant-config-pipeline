#!/usr/bin/env python3
"""Reject likely credentials, private runtime state, and unsafe repository files."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {".storage", ".cloud", ".cache", "backups", "backup", "ssl", "tts", "zigbee2mqtt"}
FORBIDDEN_NAMES = {"secrets.yaml", ".env", "known_devices.yaml", "ip_bans.yaml", ".shopping_list.json"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".key", ".pem", ".p12", ".pfx", ".jks", ".keystore", ".zip"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "credential URL": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@"),
    "JWT-like token": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
}
LITERAL_SECRET = re.compile(r"^\s*[\w-]*(?:password|passwd|token|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key)[\w-]*\s*:\s*(?![!$<{]|null\s*$|~\s*$)[^#\s].+", re.I | re.M)
SKIP_SELF = {"scripts/security_check.py", "tests/test_security_check.py"}

def candidate_files(root: Path = ROOT) -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=root)
    return [root / item.decode() for item in output.split(b"\0") if item]

def scan(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    for path in candidate_files(root):
        rel = path.relative_to(root)
        name = rel.as_posix()
        if name in SKIP_SELF:
            continue
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            findings.append(f"forbidden runtime/private path: {name}")
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden sensitive file: {name}")
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            findings.append(f"file exceeds 10 MiB: {name}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"binary file is not allowed: {name}")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"possible {label}: {name}")
        if path.suffix.lower() in {".yaml", ".yml", ".json"} and LITERAL_SECRET.search(text):
            findings.append(f"possible literal secret assignment: {name}")
    return findings

def main() -> int:
    findings = scan()
    if findings:
        print("SECURITY CHECK FAILED")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("SECURITY CHECK PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
