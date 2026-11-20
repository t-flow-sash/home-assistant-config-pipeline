# Architektur und Vertrauensgrenzen

## Drei Betriebsmodelle, ein PR-Vertrag

In allen drei Modellen führt jede Änderung über Branch oder Worktree, Pull Request, CI, menschliche Prüfung und Merge nach `main`:

1. **Eigene Agenten + eigene lokale Runner:** Eigene Agenten bearbeiten Clone oder Worktree. CI darf auf eigenen, isolierten lokalen CI-Runnern laufen. Für Deployment ist optional ein davon strikt getrennter lokaler Deployment-Runner mit fester Bridge zulässig.
2. **Desktop-only ohne eigene Runner:** Claude Desktop, Codex oder ein Editor bereitet den PR lokal vor. Der mitgelieferte Workflow läuft auf einem kurzlebigen GitHub-gehosteten Runner (`ubuntu-latest`). Nach dem menschlichen Merge folgt die vollständige [manuelle lokale Bereitstellung](deployment.md). Es ist kein eigener Runner nötig.
3. **Hybrid Desktop-Agent + GitHub Actions:** Der Desktop-Agent bearbeitet Clone oder Worktree und endet beim PR. Ein GitHub-gehosteter Runner validiert. Optional erreicht ein manueller `workflow_dispatch` nach dem Merge einen kleinen, dedizierten lokalen Self-hosted Deployment-Runner und dessen feste Bridge. Ein dauerhaft eigener KI-Agent ist nicht nötig.

### Vergleich der drei Betriebsmodelle

| Modell | Agent | CI | Deployment | Eigener Runner nötig |
| --- | --- | --- | --- | --- |
| Eigene Agenten + eigene lokale Runner | eigener Agent oder Editor | eigene isolierte lokale CI-Runner | manuell oder über getrennten lokalen Deployment-Runner/Bridge | ja, für lokale CI; Deployment-Runner optional |
| Desktop-only ohne eigene Runner | Claude Desktop, Codex oder Editor im lokalen Clone/Worktree | GitHub-gehostet auf `ubuntu-latest` | geprüfte einzelne Dateien manuell lokal übertragen | nein |
| Hybrid Desktop-Agent + GitHub Actions | Desktop-Agent im lokalen Clone/Worktree | GitHub-gehostet auf `ubuntu-latest` | optional manueller `workflow_dispatch` über lokalen Deployment-Runner/Bridge | nur für optionales Deployment |

**GitHub-gehostet** bezeichnet kurzlebige Runner von GitHub. **Self-hosted** bezeichnet eigene lokale Runner. Ein GitHub-gehosteter Runner greift niemals direkt auf Heimnetz oder Home Assistant zu. Ein lokaler CI-Runner und ein lokaler Deployment-Runner sind trotz gleicher Technik verschiedene Vertrauensrollen und dürfen nicht zusammengelegt werden.

Der jeweilige CI-Runner erhält ausschließlich den Inhalt des Repositorys. Er parst die Home-Assistant-YAML-Dateien, sucht nach privaten Dateien, Laufzeitzuständen und wahrscheinlichen Zugangsdaten, führt die Pipeline-eigenen Tests genau einmal aus und wählt bei Bedarf eigene Vertragstests aus. Gitleaks prüft bei jedem Lauf den Arbeitsbaum; bei sicherheitsrelevanten Änderungen wird zusätzlich der vollständige Git-Verlauf geprüft. Alle Berechtigungen sind schreibgeschützt. Der CI-Runner hat weder Netzwerkweg noch Zugangsdaten zu Home Assistant.

Ein optionaler Desktop-Agent liegt vor GitHub in derselben Vertrauenszone wie der lokale Editor. Er darf ausschließlich einen Clone oder isolierten Worktree bearbeiten und einen Branch samt Pull Request vorbereiten. Er erhält weder Live-Mount noch Secrets, Home-Assistant-Zugang, Runner- oder Deployment-Rechte. Details stehen unter [Claude Desktop und Codex als lokale Bearbeitungsoberflächen](desktop-agents.md).

## Zwei Wege der Bereitstellung nach dem Merge

Die drei Modelle münden in zwei sichere Endpfade. Beim Desktop-only-Pfad aktualisiert eine zuständige Person auf einem vertrauenswürdigen Rechner das lokale `main`, prüft Commit und vollständiges Backup, vergleicht und überträgt nur die vorgesehenen einzelnen Dateien und führt auf derselben Instanz die native Home-Assistant-Konfigurationsprüfung aus. Erst danach darf der betroffene Bereich neu geladen werden; ein Restart erfolgt nur, wenn er erforderlich ist. Live-Readback und bei Bedarf Rollback aus geprüften Dateien oder Backup plus Git-Revert-PR schließen den Vorgang ab.

Im Hybridmodell und im Modell mit eigenen Agenten kann stattdessen ein manueller `workflow_dispatch` nach dem Merge den getrennten lokalen Deployment-Runner erreichen. Die Autorisierung bleibt lokal: feste Bridge, Modus `preview` oder `apply`, exakter `main`- und CI-SHA, exklusives Lock, wiederherstellbares Backup, native Prüfung und Rollback. Der Actions-Workspace ist nie die Quelle für das Deployment. Beide Endpfade sind manuell; keiner wird vom Pull-Request-Workflow oder Desktop-Agenten gestartet.

## Bedrohungsmodell

Ein Pull Request kann Workflows oder Skripte verändern. Sein Code ist daher nicht vertrauenswürdig. Verbinde normale Pull-Request-Workflows niemals mit einem weitreichend berechtigten Self-hosted Runner oder mit Home-Assistant-Zugangsdaten. Wer eigene CI-Runner nutzt, isoliert sie vom Deployment-Runner und vom Zielsystem. Der Desktop-Agent erhält niemals Zugriff auf Live-Mount, Credentials oder Deployment. Eine erfolgreiche statische Prüfung sagt nichts darüber aus, ob installierte benutzerdefinierte Integrationen verfügbar sind, Geräte erreichbar sind, zeitliche Abläufe stimmen oder physische Sicherheit gewährleistet ist. Manuelles Review und eine Funktionskontrolle nach der Bereitstellung bleiben Pflicht.

## Risikobasierte Vertragstests

Die Testauswahl betrachtet die geänderten Zeilen und den zugehörigen obersten YAML-Block. Dort gefundene stabile IDs oder Entities werden mit den Dateien unter `tests/test_*.py` abgeglichen. So verbleiben anwendungsspezifische Verhaltenstests im eigenen Repository, während diese Vorlage allgemein nutzbar bleibt. Grundlegendes Parsen, Sicherheitsprüfungen, Pipeline-Unit-Tests und Gitleaks laufen immer.
