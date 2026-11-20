# Security and privacy checklist

Before any first push—and again before making your derived repository public—verify:

- [ ] no `.storage`, `.cloud`, `secrets.yaml`, databases, backups, logs, keys, certificates, `.env`, media, or integration state is tracked;
- [ ] no real hostnames, LAN/public addresses, user names, device/entity names, webhook IDs, serials, tokens, or repository history was copied unintentionally;
- [ ] every YAML credential reference uses `!secret`; the actual value exists only on the HA host;
- [ ] `python scripts/security_check.py` passes;
- [ ] `gitleaks git --redact .` and `gitleaks dir --redact .` pass locally or in Actions;
- [ ] Actions has read-only contents permission and no HA/network secrets;
- [ ] deploy happens only after review/merge from trusted local infrastructure, by copying individually reviewed files rather than bulk-replacing `/config`;
- [ ] a tested backup and rollback path exists.

Documentation uses placeholders such as `YOUR-NAME` and `/path/to/...`. Replace them locally; never commit credentials. If a secret was ever committed, deleting the file is insufficient: revoke/rotate it immediately and clean history before publication.
