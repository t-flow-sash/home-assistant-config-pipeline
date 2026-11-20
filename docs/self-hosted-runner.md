# Optional self-hosted runner

The supplied workflow intentionally uses `ubuntu-latest`, the safest beginner default. A self-hosted runner is optional and is **not** required for local deployment.

If you switch:

1. Use GitHub **Settings → Actions → Runners → New self-hosted runner**; copy current commands from GitHub rather than documentation.
2. Use a dedicated, disposable, unprivileged machine/account and a repository-specific label you choose.
3. Give it no access to `/config`, backups, SSH keys, HA tokens, LAN admin interfaces, or unrelated repositories.
4. Change only `runs-on` after reviewing the threat model.
5. Keep pinned actions and all tests unchanged.
6. Do not run untrusted fork PRs automatically; require explicit approval and prefer ephemeral runners.

Never reuse the Home Assistant host as a general PR runner. Workflow code can execute arbitrary commands with the runner user's privileges. Runner registration tokens must never be committed or pasted into issues/logs.
