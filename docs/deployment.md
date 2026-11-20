# Manual local deployment and rollback

Deployment is optional and deliberately separate from GitHub Actions. This starter does **not** provide a generic script that writes to a live Home Assistant configuration: installation paths, mounts, permissions, validation targets, and backup mechanisms differ too much to automate safely.

## Preconditions

- use a trusted local machine and a clean checkout of reviewed `main`;
- fetch first and confirm `git rev-parse HEAD` equals `git rev-parse origin/main`;
- know exactly which live Home Assistant instance and configuration directory you are changing;
- create a current encrypted **full Home Assistant backup** and verify that it is visible and restorable;
- record the current commit and the exact files you intend to change;
- stop if source, destination, backup, or validation target is ambiguous.

## Manual preflight

1. Review the merged change with `git show --stat --oneline HEAD` and `git show HEAD -- path/to/file`.
2. Run `./scripts/validate.sh --all` in the checkout.
3. In Home Assistant, create and verify a full backup before copying anything.
4. Compare each intended source file with its live counterpart using a read-only diff tool. Never point a recursive copy or delete command at `/config`.
5. Confirm that omitted repository files are intentional. Absence in Git is **not** an instruction to delete a live file.

## Manual apply and native check

1. Copy only the individually reviewed files through your installation's supported editor, Samba share, or SSH path. Do not bulk-replace `/config`, `.storage`, secrets, databases, or integration state.
2. Preserve ownership and permissions appropriate to your installation.
3. Run **Developer tools → YAML → Check configuration** on that same Home Assistant instance (or `ha core check` only when the CLI is demonstrably attached to that instance).
4. If the check fails, do not reload or restart. Restore the affected files from the verified backup and check again.
5. After a successful check, reload only the affected domain. Restart only when Home Assistant explicitly requires it.
6. Verify changed entities, automation traces, logs, and physical behavior.

## Manual rollback

1. Stop further changes and note the failed commit and symptoms.
2. Restore the affected files—or the full backup when scope is uncertain—using Home Assistant's supported restore path.
3. Run **Check configuration** against the restored instance before any reload or restart.
4. Verify runtime behavior and logs.
5. Create a Git revert PR so the repository and live system converge. A Git revert alone does not undo deployed files; a backup restore alone leaves repository drift.

Machine-specific deployment automation belongs in the derived private repository only after it has installation-specific path validation, transactional staging, verified backups, and tested recovery. Do not generalize it back into this starter.
