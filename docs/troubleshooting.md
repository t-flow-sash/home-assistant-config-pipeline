# Troubleshooting

## No Home Assistant YAML found

Expected in a fresh template. Add your own `configuration.yaml`, `automations.yaml`, `packages/`, or another supported path. No example config is intentionally shipped.

## Included file/directory does not exist

The parser follows `!include` paths relative to the containing file. Commit non-sensitive included YAML or correct the path. Never add a fake secret file just to satisfy CI.

## Literal secret assignment

Move the value to ignored `secrets.yaml` on HA and reference it with `!secret`. For a false positive, redesign the example/name rather than broadly disabling scanning.

## Gitleaks reports a finding

Treat it as real until disproved. Revoke and rotate exposed credentials first. A later deletion does not remove Git history. Use a narrowly documented allowlist only for a demonstrable false positive.

## GitHub is green but HA rejects configuration

CI understands common YAML tags but cannot know your installed HA version/integrations. Stop deployment and run native `ha core check` against the actual installation. Restore the pre-deploy backup on failure.

## How do I deploy?

There is intentionally no generic live-write helper. Follow the manual checklist in `docs/deployment.md`: confirm reviewed `main`, verify a full backup, compare and copy only intended files, and run the native configuration check against the same Home Assistant instance. Never bulk-replace `/config`.

## No focused user test was selected

That is valid for a new normal area: baseline checks still ran. Document the manual functional test in the PR. Add a focused contract when a stable ID/entity can protect important behavior.
