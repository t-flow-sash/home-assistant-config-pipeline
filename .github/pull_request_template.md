## Purpose

<!-- What changes, and why? -->

## Scope and risk

- [ ] Normal configuration/documentation change
- [ ] Security-sensitive: auth/HTTP/proxy, shell/command, webhook, alarm/lock, credentials, CI, or deployment
- Affected HA areas/entities (no private values):

## Verification

- [ ] `./scripts/validate.sh --all` passed locally, or I explained why not
- [ ] I reviewed the complete diff for secrets and runtime/private files
- [ ] I described a manual functional check for the real HA instance
- [ ] Native `ha core check` / **Check configuration** will run before reload/restart

## Deployment

- [ ] No deployment required
- [ ] Reload affected domain(s)
- [ ] Controlled restart required

## Rollback

<!-- Name the exact files/commit and how the pre-deploy backup will be restored. -->
