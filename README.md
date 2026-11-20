# Home Assistant Config Pipeline

Eine wiederverwendbare, sicherheitsbewusste Vorlage, mit der du **deine eigene** Home-Assistant-YAML-Konfiguration über GitHub Pull Requests verwaltest. Änderungen werden auf einem von GitHub gehosteten Runner geprüft. Die Vorlage beschreibt außerdem die bewusst manuelle lokale Bereitstellung, die native Konfigurationsprüfung von Home Assistant und den Rollback.

> **Dieses Repository enthält bewusst keine Home-Assistant-Konfiguration.** Erstelle aus der Vorlage ein neues Repository, lasse es bis zum Abschluss der Datenschutz-Checkliste privat und versioniere anschließend nur die YAML-Dateien, die du gezielt ausgewählt hast.

## Funktionsumfang

- Home-Assistant-YAML wird bei jedem Lauf geparst, einschließlich der üblichen Tags `!include`, `!secret` und `!input` für Blueprints;
- typische Laufzeit- und private Dateien sowie wahrscheinlich im Klartext hinterlegte Zugangsdaten werden abgewiesen;
- passende, eigene Verhaltenstests werden risikobasiert ausgewählt;
- Gitleaks läuft bei jedem Pull Request und bei jedem Push auf `main`;
- der GitHub-Actions-Workflow verwendet festgeschriebene Action-Versionen, minimale Berechtigungen und `ubuntu-latest`;
- die Pull-Request-Checkliste deckt Risiko, Tests, Bereitstellung und Rollback ab;
- die lokale Prüfung startet mit einem einzigen Befehl;
- die Checkliste für die manuelle Bereitstellung sorgt dafür, dass GitHub weder Home-Assistant- noch LAN-Zugangsdaten benötigt.

## Architektur

```text
Editor → Branch → GitHub-PR → statische Prüfung/Review → Merge nach main
                                                               │ git pull
                                                               ▼
                                     vertrauenswürdiger Rechner im eigenen Netz
                                     geprüftes Backup → geprüfte Dateien kopieren → HA-Prüfung
                                                                          ↘ manueller Rollback
```

Der Pull-Request-Workflow stellt **niemals** Konfiguration bereit und benötigt keinen Zugriff auf Home Assistant. Weitere Einzelheiten stehen unter [Architektur und Vertrauensgrenzen](docs/architecture.md). Optional kann ein davon getrennter, ausschließlich manueller Workflow einen lokalen Vertrauensanker anstoßen; er führt keinen PR-Code aus und schreibt nicht selbst in Home Assistant.

## Schnellstart

1. Klicke auf GitHub auf **Use this template** und erstelle ein **privates** Repository.
2. Klone das Repository und installiere die Prüfwerkzeuge:

```bash
git clone https://github.com/DEIN-NAME/DEIN-REPOSITORY.git
cd DEIN-REPOSITORY
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

3. Füge deine eigene Home-Assistant-YAML-Konfiguration hinzu, zum Beispiel `configuration.yaml` und die darin eingebundenen Dateien. Kopiere **nicht** den gesamten Inhalt von `/config`. Dateien und Verzeichnisse wie `.storage/`, `secrets.yaml`, Datenbanken, Backups, Schlüssel, Protokolle oder Integrationszustände gehören nie ins Repository.
4. Lege geheime Werte ausschließlich in der ignorierten Datei `secrets.yaml` auf dem Home-Assistant-System ab und binde sie mit `!secret` ein.
5. Prüfe alles vor dem ersten Push:

```bash
./scripts/validate.sh --all
```

Eine leere Vorlage ist gültig. Solange noch keine Home-Assistant-YAML-Datei vorhanden ist, gibt die Prüfung einen Hinweis aus.

## Pull-Request-Ablauf

```bash
git switch -c fix/beispiel-aenderung
# Eigene YAML-Dateien bearbeiten.
./scripts/validate.sh --all
git add --all
git diff --cached
git commit -m "fix(ha): Änderung beschreiben"
git push -u origin HEAD
```

Öffne einen Pull Request und fülle die mitgelieferte Vorlage aus. GitHub Actions verwendet keine Repository-Secrets. Schütze `main` nach dem ersten erfolgreichen Lauf und fordere den Check **Vorlage und Home-Assistant-Konfiguration prüfen / validate** verpflichtend an.

## Lokale Bereitstellung

Stelle niemals aus einem Pull-Request-Workflow bereit. Diese Vorlage enthält bewusst kein allgemeines Skript, das in eine laufende Installation schreibt. Folge zunächst [Manuelle lokale Bereitstellung und Rollback](docs/deployment.md): Prüfe ein vollständiges Backup, vergleiche und kopiere ausschließlich die freigegebenen Dateien, führe die Home-Assistant-eigene Konfigurationsprüfung auf genau dieser Instanz aus und lade anschließend nur die betroffenen Bereiche neu.

Wenn dieser Ablauf erprobt ist, zeigt [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](docs/github-triggered-deployment.md), wie ein `workflow_dispatch` auf `main` sicher einen dedizierten Runner im Heimnetz erreicht. GitHub bleibt Auslöser; eine feste root-eigene Bridge übernimmt nur einen grünen `origin/main`-SHA, sperrt parallele Läufe, erstellt ein Backup und rollt bei fehlgeschlagener nativer Prüfung zurück. Sichere Voreinstellung ist `preview`; auch `apply` führt keinen automatischen Reload oder Restart aus.

## Gezielte Verhaltenstests

Statisches Parsen kann das Verhalten einer Automation nicht beweisen. Ergänze für wichtiges Verhalten einen kleinen Vertragstest unter `tests/test_*.py` und nenne darin eine stabile Automations-`id`, `unique_id` oder Entity-ID. Ändert sich der zugehörige YAML-Block, wählt `scripts/select_ci_checks.py` den passenden Test aus. Geänderte eigene Vertragstests werden direkt ausgeführt; die zur Pipeline gehörenden Tests laufen in jedem CI-Lauf genau einmal. `./scripts/validate.sh --all` führt lokal alle Tests aus.

## Dokumentation

- [Schnellstart und Voraussetzungen](docs/quickstart.md)
- [Architektur und Vertrauensgrenzen](docs/architecture.md)
- [Sicherheits- und Datenschutz-Checkliste](docs/security.md)
- [Lokale Bereitstellung und Rollback](docs/deployment.md)
- [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](docs/github-triggered-deployment.md)
- [Optionaler selbst gehosteter Runner](docs/self-hosted-runner.md)
- [Fehlerbehebung](docs/troubleshooting.md)

## Nicht vorgesehen

Dieses Projekt liefert keine Home-Assistant-Konfiguration aus, speichert keine Zugangsdaten oder Laufzeitzustände, stellt keinen ungeprüften Code bereit, ersetzt nicht die native Prüfung mit `check_config` und kann das Verhalten physischer Geräte nicht nachweisen.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
