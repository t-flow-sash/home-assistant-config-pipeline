# Architecture and trust boundaries

## Pull-request path

The hosted GitHub runner receives only repository content. It parses HA YAML, scans for private/runtime files and likely credentials, runs pipeline-owned tests exactly once, and selects optional user contract tests. Gitleaks scans the working tree on every run; security-sensitive changes additionally trigger a full-history scan. Permissions are read-only. The runner has no route or credential to Home Assistant.

## Deployment path

Only a trusted machine on the same controlled network as Home Assistant pulls reviewed `main`. This starter has no generic live-write helper. An operator verifies the exact commit and a restorable full backup, compares and copies only intended files, and invokes Home Assistant's native configuration check against that same instance before a narrow reload. Rollback is manual through the installation's supported restore path.

## Threat model

A PR can modify workflow or scripts, so PR code is untrusted. Never attach a broadly privileged self-hosted runner or HA credentials to normal PR workflows. A green static check does not validate installed custom integrations, device availability, timing, or physical safety. Human review and post-deploy readback remain required.

## Risk-based contracts

The selector looks at changed lines and the containing top-level YAML block. Stable IDs/entities found there are matched against `tests/test_*.py`. This keeps user-specific behavior contracts in the user's repository while this template stays generic. Baseline parsing, security checks, pipeline unit tests, and Gitleaks always run.
