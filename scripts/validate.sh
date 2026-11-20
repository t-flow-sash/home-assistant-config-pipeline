#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
BASE="origin/main"
ALL=false
while (($#)); do
  case "$1" in
    --base) BASE="${2:?--base requires a commit}"; shift 2 ;;
    --all) ALL=true; shift ;;
    *) echo "Usage: $0 [--base COMMIT] [--all]" >&2; exit 2 ;;
  esac
done
python3 -m venv .venv
.venv/bin/python -m pip install --quiet --disable-pip-version-check --require-hashes -r requirements.txt
.venv/bin/python scripts/validate_ha_yaml.py
.venv/bin/python scripts/security_check.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
if git rev-parse --verify "$BASE^{commit}" >/dev/null 2>&1; then
  git diff --check "$BASE"...HEAD
elif [[ "$ALL" != true ]]; then
  echo "Base $BASE is unavailable; use --all for a fresh repository." >&2
  exit 2
fi
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --redact .
  gitleaks dir --redact .
else
  echo "NOTE: gitleaks is not installed locally; GitHub Actions performs the scan."
fi
echo "VALIDATION PASSED"
