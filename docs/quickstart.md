# Schnellstart und Voraussetzungen

## Voraussetzungen

- Git, Python 3.11 oder neuer und ein GitHub-Konto;
- ein **privates** Repository, das aus dieser Vorlage erstellt wurde;
- kontrollierter Zugriff von einem vertrauenswürdigen lokalen Rechner auf das Home-Assistant-Verzeichnis `/config`;
- ein aktuelles, verschlüsseltes Home-Assistant-Backup;
- ausreichende Home-Assistant-Kenntnisse, um **Konfiguration prüfen** auszuführen, betroffene Bereiche neu zu laden und Automations-Traces auszuwerten.

Für CI werden weder GitHub-Secret noch Home-Assistant-Token, SSH-Schlüssel, LAN-Adresse oder Runner-Registrierungstoken benötigt.

## Ersteinrichtung

1. Erstelle über **Use this template** ein privates Repository.
2. Klone es, erstelle `.venv` und installiere die Abhängigkeiten aus `requirements.txt`.
3. Füge nur bewusst ausgewählte YAML-Dateien hinzu. Diese Vorlage liefert keine Home-Assistant-Konfiguration mit.
4. Belasse `secrets.yaml` und sämtliche Laufzeitzustände auf dem Home-Assistant-System.
5. Führe `./scripts/validate.sh --all` aus.
6. Pushe einen Branch und öffne einen Pull Request.
7. Lege nach dem ersten erfolgreichen Lauf eine Regel für den Branch `main` an, die den Validierungsjob verpflichtend macht.
8. Die Bereitstellung bleibt lokal und manuell. Diese Vorlage enthält bewusst kein allgemeines Skript, das in das laufende Verzeichnis `/config` schreibt. Teste Backup und Rollback vor der ersten Änderung.
9. Optional und erst nach dieser Abnahme: Richte einen manuellen GitHub-Trigger nach [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](github-triggered-deployment.md) ein. Beginne nur mit `preview`; aktiviere `apply` nie vor einem nachgewiesenen Backup-/Rollback-Test.

Ein GitHub-gehosteter Runner soll dafür **keinen** direkten Zugang zum Heimnetz erhalten. Für die optionale Variante bleibt die Validierung auf `ubuntu-latest`; nur der manuelle Deployment-Job wird an einen dedizierten lokalen Runner geroutet. Dieser Runner darf weder Pull-Request-Code ausführen noch direkt in die Home-Assistant-Konfiguration schreiben.

## Empfohlene Struktur des eigenen Repositorys

```text
configuration.yaml       # deine Datei, hier nicht mitgeliefert
automations.yaml         # deine Datei, optional
packages/                # deine Dateien, optional
tests/test_*.py          # gezielte Verhaltenstests, optional
```

Kopiere `/config` niemals gesammelt in Git. Beginne mit einer einzelnen geprüften Datei und erweitere den Umfang schrittweise.
