# Sicherheits- und Datenschutz-Checkliste

Prüfe vor dem ersten Push und erneut, bevor du dein abgeleitetes Repository veröffentlichst:

- [ ] Es werden keine Dateien oder Verzeichnisse wie `.storage`, `.cloud`, `secrets.yaml`, Datenbanken, Backups, Protokolle, Schlüssel, Zertifikate, `.env`, Medien oder Integrationszustände versioniert.
- [ ] Es wurden keine echten Hostnamen, LAN- oder öffentlichen Adressen, Benutzernamen, Geräte- oder Entity-Namen, Webhook-IDs, Seriennummern, Token oder Teile eines anderen Repository-Verlaufs unbeabsichtigt übernommen.
- [ ] Jede Referenz auf Zugangsdaten in YAML verwendet `!secret`; der tatsächliche Wert liegt ausschließlich auf dem Home-Assistant-System.
- [ ] `python scripts/security_check.py` läuft erfolgreich durch.
- [ ] `gitleaks git --redact .` und `gitleaks dir --redact .` laufen lokal oder in GitHub Actions erfolgreich durch.
- [ ] GitHub Actions hat nur Leserechte auf den Repository-Inhalt und erhält keine Home-Assistant- oder Netzwerk-Secrets.
- [ ] Die Bereitstellung erfolgt erst nach Review und Merge aus einer vertrauenswürdigen lokalen Umgebung. Dabei werden nur einzeln geprüfte Dateien kopiert; `/config` wird niemals gesammelt ersetzt.
- [ ] Ein getestetes Backup- und Rollback-Verfahren ist vorhanden.

Die Dokumentation verwendet Platzhalter wie `DEIN-NAME` und `/path/to/...`. Ersetze sie nur lokal und committe niemals Zugangsdaten. Wurde ein Secret irgendwann eingecheckt, reicht das Löschen der Datei nicht aus: Sperre oder rotiere den Wert sofort und bereinige den Git-Verlauf vor der Veröffentlichung.
