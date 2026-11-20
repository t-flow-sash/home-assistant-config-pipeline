# Schnellstart und Voraussetzungen

## Voraussetzungen

- Git, Python 3.11 oder neuer und ein GitHub-Konto;
- ein **privates** Repository, das aus dieser Vorlage erstellt wurde;
- kontrollierter Zugriff von einem vertrauenswürdigen lokalen Rechner auf das Home-Assistant-Verzeichnis `/config`;
- ein aktuelles, verschlüsseltes Home-Assistant-Backup;
- ausreichende Home-Assistant-Kenntnisse, um **Konfiguration prüfen** auszuführen, betroffene Bereiche neu zu laden und Automations-Traces auszuwerten.

Im Desktop-only- und Hybridmodell werden für die GitHub-gehostete CI weder GitHub-Secret noch Home-Assistant-Token, SSH-Schlüssel, LAN-Adresse oder Runner-Registrierungstoken benötigt. Nutzer mit eigenen Agenten können den Validierungsworkflow bewusst auf eigene isolierte lokale CI-Runner umstellen; auch diese erhalten keinen Home-Assistant-Zugriff.

Wähle eines der drei Modelle: **eigene Agenten + eigene lokale Runner**, **Desktop-only ohne eigene Runner** oder **Hybrid Desktop-Agent + GitHub Actions**. Die Unterschiede sind in der [Vergleichstabelle](architecture.md#vergleich-der-drei-betriebsmodelle) zusammengefasst.

## Ersteinrichtung

1. Erstelle über **Use this template** ein privates Repository.
2. Klone es, erstelle `.venv` und installiere die Abhängigkeiten aus `requirements.txt`.
3. Füge nur bewusst ausgewählte YAML-Dateien hinzu. Diese Vorlage liefert keine Home-Assistant-Konfiguration mit.
4. Belasse `secrets.yaml` und sämtliche Laufzeitzustände auf dem Home-Assistant-System.
5. Führe `./scripts/validate.sh --all` aus.
6. Pushe einen Branch und öffne einen Pull Request.
7. Lege nach dem ersten erfolgreichen Lauf eine Regel für den Branch `main` an, die den Validierungsjob verpflichtend macht.
8. **Desktop-only:** Folge nach jedem Merge vollständig der [manuellen lokalen Bereitstellung](deployment.md). Aktualisiere zuerst dein lokales `main`, erstelle ein vollständiges Home-Assistant-Backup, übertrage nur einzeln geprüfte Dateien, führe die native Konfigurationsprüfung aus, lade nur den betroffenen Bereich neu und lies den Live-Zustand zurück. Dafür ist kein selbst gehosteter Runner nötig.
9. **Hybrid:** Richte optional und erst nach erprobtem Backup und Rollback den [manuellen GitHub-Trigger mit lokalem Vertrauensanker](github-triggered-deployment.md) ein. Der Desktop-Agent endet weiterhin beim PR und GitHub-gehostete CI validiert; nur `workflow_dispatch` nutzt den dedizierten lokalen Deployment-Runner. Beginne mit `preview`.
10. **Eigene Agenten + eigene lokale Runner:** Du darfst CI auf isolierte lokale CI-Runner verlegen und zusätzlich einen strikt getrennten Deployment-Runner einsetzen. Vermische beide Rollen nie.

Wenn du Claude Desktop oder Codex in der ChatGPT-Desktop-App als Editor verwenden möchtest, richte zuerst den Clone ein und folge dann [Desktop-Agenten sicher verwenden](desktop-agents.md). Der Agent erhält nur den Clone oder einen Worktree, niemals `/config` oder Secrets, und endet mit einem Pull Request.

Ein GitHub-gehosteter Runner soll **keinen** direkten Zugang zum Heimnetz erhalten. Im mitgelieferten Desktop-only- und Hybridstandard bleibt die Validierung auf `ubuntu-latest`. Nur im Modell mit eigenen Agenten darf CI auf eigenen lokalen Runnern laufen, sofern CI- und Deployment-Rolle getrennt bleiben. Der Deployment-Runner darf weder Pull-Request-Code ausführen noch direkt in die Home-Assistant-Konfiguration schreiben.

## Empfohlene Struktur des eigenen Repositorys

```text
configuration.yaml       # deine Datei, hier nicht mitgeliefert
automations.yaml         # deine Datei, optional
packages/                # deine Dateien, optional
tests/test_*.py          # gezielte Verhaltenstests, optional
```

Kopiere `/config` niemals gesammelt in Git. Beginne mit einer einzelnen geprüften Datei und erweitere den Umfang schrittweise.
