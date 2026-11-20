# Manuelle lokale Bereitstellung und Rollback

Die Bereitstellung ist optional und bewusst vom Pull-Request-Workflow getrennt. Diese Vorlage enthält **kein** allgemeines Skript, das in eine laufende Home-Assistant-Konfiguration schreibt: Installationspfade, Mounts, Berechtigungen, Prüfziele und Backup-Verfahren unterscheiden sich zu stark, um sie sicher zu automatisieren.

Diese Grenze gilt auch für [Claude Desktop und Codex in der Desktop-App](desktop-agents.md): Sie dürfen Änderungen nur lokal in Branch oder Worktree bis zum Pull Request vorbereiten. Sie bekommen keinen Zugriff auf `/config`, die lokale Bridge oder den manuellen Deployment-Trigger.

Dieser Ablauf ist die empfohlene Grundlage für Einsteiger. Wenn Backup und Rollback damit bereits erprobt sind, kann [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](github-triggered-deployment.md) einen GitHub-Button ergänzen. Auch dort schreibt nicht der Workflow: Eine feste lokale Bridge entscheidet anhand von `main`, exaktem CI-SHA und lokaler Policy.

## Voraussetzungen

- Verwende einen vertrauenswürdigen lokalen Rechner und einen sauberen Checkout des geprüften Branches `main`;
- rufe zuerst die Remote-Änderungen ab und bestätige, dass `git rev-parse HEAD` und `git rev-parse origin/main` denselben Wert liefern;
- stelle zweifelsfrei fest, welche laufende Home-Assistant-Instanz und welches Konfigurationsverzeichnis geändert werden;
- erstelle ein aktuelles, verschlüsseltes **vollständiges Home-Assistant-Backup** und prüfe, ob es sichtbar und wiederherstellbar ist;
- notiere den aktuellen Commit und die Dateien, die geändert werden sollen;
- brich ab, sobald Quelle, Ziel, Backup oder Prüfziel nicht eindeutig sind.

## Manuelle Vorprüfung

1. Prüfe die zusammengeführte Änderung mit `git show --stat --oneline HEAD` und `git show HEAD -- path/to/file`.
2. Führe im Checkout `./scripts/validate.sh --all` aus.
3. Erstelle und prüfe in Home Assistant ein vollständiges Backup, bevor du Dateien kopierst.
4. Vergleiche jede vorgesehene Quelldatei mit ihrem Gegenstück in der laufenden Installation. Verwende dazu ein Werkzeug, das nur lesend zugreift. Richte niemals einen rekursiven Kopier- oder Löschbefehl auf `/config`.
5. Vergewissere dich, dass im Repository fehlende Dateien bewusst ausgelassen wurden. Eine in Git fehlende Datei ist **keine** Aufforderung, die entsprechende Datei in der laufenden Installation zu löschen.

## Manuelles Einspielen und native Prüfung

1. Kopiere ausschließlich einzeln geprüfte Dateien. Verwende dafür den von deiner Installation unterstützten Editor, eine Samba-Freigabe oder den SSH-Zugriff. Ersetze niemals gesammelt `/config`, `.storage`, Secrets, Datenbanken oder Integrationszustände.
2. Erhalte die für deine Installation vorgesehenen Eigentümer und Dateiberechtigungen.
3. Führe auf derselben Home-Assistant-Instanz **Entwicklerwerkzeuge → YAML → Konfiguration prüfen** aus. Verwende `ha core check` nur, wenn die CLI nachweislich mit genau dieser Instanz verbunden ist.
4. Schlägt die Prüfung fehl, darfst du weder neu laden noch neu starten. Stelle die betroffenen Dateien aus dem geprüften Backup wieder her und prüfe erneut.
5. Lade nach erfolgreicher Prüfung nur den betroffenen Bereich neu. Starte Home Assistant ausschließlich dann neu, wenn es ausdrücklich erforderlich ist.
6. Prüfe die geänderten Entities, Automations-Traces, Protokolle und das Verhalten der physischen Geräte.

## Manueller Rollback

1. Stoppe weitere Änderungen und notiere den fehlgeschlagenen Commit sowie die beobachteten Symptome.
2. Stelle die betroffenen Dateien über den von Home Assistant unterstützten Weg wieder her. Ist der Umfang unklar, verwende das vollständige Backup.
3. Führe auf der wiederhergestellten Instanz **Konfiguration prüfen** aus, bevor du etwas neu lädst oder neu startest.
4. Prüfe Laufzeitverhalten und Protokolle.
5. Erstelle einen Git-Revert-Pull-Request, damit Repository und laufendes System wieder denselben Stand erreichen. Ein Git-Revert macht bereits bereitgestellte Dateien nicht rückgängig; eine Backup-Wiederherstellung allein beseitigt die Abweichung im Repository nicht.

Rechnerspezifische Automatisierung für die Bereitstellung gehört erst dann in das abgeleitete private Repository, wenn sie installationsspezifische Pfadprüfungen, transaktionales Staging, geprüfte Backups und eine erprobte Wiederherstellung umfasst. Übertrage eine solche Lösung nicht verallgemeinert zurück in diese Vorlage.

Für eine GitHub-ausgelöste Variante veröffentliche ebenfalls keinen generischen Writer. Dokumentiere stattdessen die schmale Schnittstelle (`preview`/`apply`) und prüfe den vollständigen [Bridge-Vertrag und die Abnahme-Checkliste](github-triggered-deployment.md#verbindlicher-bridge-vertrag).
