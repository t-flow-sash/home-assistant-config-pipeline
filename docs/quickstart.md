# Quickstart and prerequisites

## Prerequisites

- Git, Python 3.11 or newer, and a GitHub account;
- a **private** repository created from this template;
- controlled access from a trusted local machine to Home Assistant's `/config`;
- a current encrypted Home Assistant backup;
- enough HA knowledge to run **Check configuration**, reload affected domains, and inspect automation traces.

No GitHub secret, HA token, SSH key, LAN address, or runner registration token is needed for CI.

## First setup

1. Create a private repository using **Use this template**.
2. Clone it, create `.venv`, and install `requirements.txt`.
3. Add only intentionally versioned YAML. This template supplies no HA configuration.
4. Keep `secrets.yaml` and all runtime state on the HA host.
5. Run `./scripts/validate.sh --all`.
6. Push a branch and open a PR.
7. Require the validation job in a `main` branch ruleset after its first successful run.
8. Keep deployment local and manual. This starter intentionally has no generic script that writes to live `/config`; test backup and rollback before the first change.

## Suggested user repository layout

```text
configuration.yaml       # yours, not supplied here
automations.yaml         # yours, optional
packages/                # yours, optional
tests/test_*.py          # focused behavior contracts, optional
```

Never bulk-copy `/config` into Git. Start with one reviewed file and grow deliberately.
