# Schnellstart und Voraussetzungen

## Voraussetzungen

- Git, Python 3.11 oder neuer und ein GitHub-Konto;
- ein **privates** Repository, das aus dieser Vorlage erstellt wurde;
- kontrollierter Zugriff von einem vertrauenswürdigen lokalen Rechner auf das Home-Assistant-Verzeichnis `/config`;
- ein aktuelles, verschlüsseltes Home-Assistant-Backup;
- ausreichende Home-Assistant-Kenntnisse, um **Konfiguration prüfen** auszuführen, betroffene Bereiche neu zu laden und Automations-Traces auszuwerten.

Im Desktop-only-Modell werden für CI weder GitHub-Secret noch Home-Assistant-Token, SSH-Schlüssel, LAN-Adresse oder Runner-Registrierungstoken benötigt. Nutzer mit eigener Infrastruktur können den Validierungsworkflow bewusst auf eigene isolierte CI-Runner umstellen; auch diese erhalten keinen Home-Assistant-Zugriff.

## Ersteinrichtung

1. Erstelle über **Use this template** ein privates Repository.
2. Klone es, erstelle `.venv` und installiere die Abhängigkeiten aus `requirements.txt`.
3. Füge nur bewusst ausgewählte YAML-Dateien hinzu. Diese Vorlage liefert keine Home-Assistant-Konfiguration mit.
4. Belasse `secrets.yaml` und sämtliche Laufzeitzustände auf dem Home-Assistant-System.
5. Führe `./scripts/validate.sh --all` aus.
6. Pushe einen Branch und öffne einen Pull Request.
7. Lege nach dem ersten erfolgreichen Lauf eine Regel für den Branch `main` an, die den Validierungsjob verpflichtend macht.
8. Wähle nach dem Merge einen der beiden Endpfade: Desktop-only folgt der [manuellen lokalen Bereitstellung](deployment.md) und benötigt keinen selbst gehosteten Runner. Diese Vorlage enthält bewusst kein allgemeines Skript, das in `/config` schreibt. Teste Backup und Rollback vor der ersten Änderung.
9. Optional für eigene Infrastruktur und erst nach dieser Abnahme: Richte einen manuellen GitHub-Trigger nach [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](github-triggered-deployment.md) ein. Dieser GitHub-Deploy-Button erfordert einen dedizierten lokalen Deployment-Runner. Beginne nur mit `preview`; aktiviere `apply` nie vor einem nachgewiesenen Backup-/Rollback-Test.

Wenn du Claude Desktop oder Codex in der ChatGPT-Desktop-App als Editor verwenden möchtest, richte zuerst den Clone ein und folge dann [Desktop-Agenten sicher verwenden](desktop-agents.md). Der Agent erhält nur den Clone oder einen Worktree, niemals `/config` oder Secrets, und endet mit einem Pull Request.

Ein GitHub-gehosteter Runner soll **keinen** direkten Zugang zum Heimnetz erhalten. Im mitgelieferten Desktop-only-Standard bleibt die Validierung auf `ubuntu-latest`. Im Modell mit eigener Infrastruktur darf auch CI auf eigenen lokalen Runnern laufen, sofern CI- und Deployment-Rolle getrennt bleiben. Der Deployment-Runner darf weder Pull-Request-Code ausführen noch direkt in die Home-Assistant-Konfiguration schreiben.

## Empfohlene Struktur des eigenen Repositorys

```text
configuration.yaml       # deine Datei, hier nicht mitgeliefert
automations.yaml         # deine Datei, optional
packages/                # deine Dateien, optional
tests/test_*.py          # gezielte Verhaltenstests, optional
```

Kopiere `/config` niemals gesammelt in Git. Beginne mit einer einzelnen geprüften Datei und erweitere den Umfang schrittweise.
