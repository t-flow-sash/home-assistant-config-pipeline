# Home Assistant Config Pipeline

A reusable, security-conscious template for managing **your own** Home Assistant YAML with GitHub pull requests. It validates changes on a GitHub-hosted runner and documents a deliberately manual local deployment, native Home Assistant validation, and rollback process.

> **This repository intentionally contains no Home Assistant configuration.** Create a repository from this template, keep it private until you have completed the privacy checklist, and then add only the YAML you deliberately want under version control.

## What you get

- always-on parsing for tracked Home Assistant YAML, including common `!include`, `!secret`, and Blueprint `!input` tags;
- rejection of common runtime/private files and likely literal credentials;
- risk-based selection of your own focused contract tests;
- Gitleaks on every PR and push to `main`;
- a pinned, least-privilege GitHub Actions workflow using `ubuntu-latest`;
- a PR checklist for risk, test, deployment, and rollback;
- local validation with one command;
- a manual deployment checklist—GitHub never receives Home Assistant or LAN credentials.

## Architecture

```text
Editor → branch → GitHub PR → static validation/review → merge to main
                                                          │ git pull
                                                          ▼
                                  trusted machine on your network
                                  verified backup → reviewed file copy → HA check
                                                              ↘ manual rollback
```

The PR workflow **never deploys** and does not need access to Home Assistant. See [Architecture and trust boundaries](docs/architecture.md).

## Quickstart

1. Click **Use this template** on GitHub and create a **private** repository.
2. Clone it and install the validator:

```bash
git clone https://github.com/YOUR-NAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

3. Add your own HA YAML, for example `configuration.yaml` and files it includes. Do **not** copy all of `/config`; never commit `.storage/`, `secrets.yaml`, databases, backups, keys, logs, or integration state.
4. Put secret values only in the ignored `secrets.yaml` on your Home Assistant host and reference them with `!secret`.
5. Validate before your first push:

```bash
./scripts/validate.sh --all
```

An empty template is valid; the validator prints a notice until you add HA YAML.

## Pull-request workflow

```bash
git switch -c fix/example-change
# Edit your own YAML.
./scripts/validate.sh --all
git add --all
git diff --cached
git commit -m "fix(ha): describe the change"
git push -u origin HEAD
```

Open a PR and complete the supplied template. GitHub Actions uses no repository secrets. After the first green run, protect `main` and require **Validate template and Home Assistant configuration / validate**.

## Local deployment

Do not deploy from a PR workflow. This starter intentionally ships no generic live-write script. Follow [Manual local deployment and rollback](docs/deployment.md): verify a full backup, compare and copy only reviewed files, run Home Assistant's own configuration check against the same instance, then reload narrowly.

## Focused behavior tests

Static parsing cannot prove automation behavior. Add a small `tests/test_*.py` contract for important behavior and mention a stable automation `id`, `unique_id`, or entity ID in that test. When the corresponding YAML block changes, `scripts/select_ci_checks.py` selects the contract. Changed user contract files run directly; pipeline-owned tests run exactly once on every CI run. `./scripts/validate.sh --all` runs all tests locally.

## Documentation

- [Quickstart and prerequisites](docs/quickstart.md)
- [Architecture and trust boundaries](docs/architecture.md)
- [Security and privacy checklist](docs/security.md)
- [Local deployment and rollback](docs/deployment.md)
- [Optional self-hosted runner](docs/self-hosted-runner.md)
- [Troubleshooting](docs/troubleshooting.md)

## Non-goals

This project does not ship HA configuration, store credentials/runtime state, deploy unreviewed code, replace native `check_config`, or prove physical device behavior.

## License

MIT — see [LICENSE](LICENSE).
