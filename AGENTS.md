# Arbeitsregeln für Desktop-Agenten

## Geltungsbereich

Diese Regeln gelten für das gesamte Repository. Lies zusätzlich `README.md` und die Dokumentation unter `docs/`.

## Sicherer Änderungsablauf

- Arbeite nur im lokalen Clone oder in einem zugehörigen Git-Worktree.
- Erstelle für jede Änderung einen eigenen Branch. Pushe niemals direkt nach `main`.
- Ändere nur Dateien, die für die konkrete Aufgabe erforderlich sind.
- Führe vor einem Commit `./scripts/validate.sh --all` aus und berichte das echte Ergebnis.
- Prüfe vor Push und Pull Request den vollständigen Diff gegen `origin/main`.
- Erfinde keine Test-, CI-, Review- oder Deployment-Ergebnisse.

## Strikte Grenzen

- Greife niemals auf das Home-Assistant-Verzeichnis `/config` oder eine laufende Home-Assistant-Instanz zu.
- Lies, erzeuge oder übertrage keine `secrets.yaml`, `.env`, Home-Assistant-Token, SMB-Zugangsdaten, SSH-Schlüssel oder andere Credentials.
- Richte keinen Home-Assistant-Connector, MCP-Server, direkten API-Zugriff oder automatische Deployment-Brücke ein.
- Starte keinen Deployment-Workflow, Reload oder Restart und führe keinen Rollback aus.
- Verwende keine Dangerous-, Full-Access- oder Approval-Bypass-Modi.
- Veröffentliche keine privaten Namen, IDs, Adressen, Hostnamen oder Daten einer Referenzinstallation.

## Liefergrenze

Ein Agent darf Branch, Diff, lokale Tests, Commit und Pull Request vorbereiten. CI und menschliche PR-Prüfung bleiben verpflichtende Gates. Nach dem Merge gibt es genau zwei dokumentierte Endpfade: die kontrollierte manuelle lokale Bereitstellung gemäß `docs/deployment.md` oder optional ein manueller `workflow_dispatch` auf `main` über einen getrennten lokalen Deployment-Runner und die feste Bridge. Der Desktop-Agent startet keinen der beiden Wege.
