# Architektur und Vertrauensgrenzen

## Zwei Betriebsmodelle, ein PR-Vertrag

In beiden Modellen führt jede Änderung über Branch oder Worktree, Pull Request, CI, menschliche Prüfung und Merge nach `main`:

- **Desktop-only ohne eigene Runner:** Ein lokaler Desktop-Agent oder Editor bereitet den Pull Request vor. Der mitgelieferte Workflow läuft auf einem kurzlebigen GitHub-gehosteten Runner. Nach dem Merge folgt die kontrollierte manuelle lokale Bereitstellung gemäß [Deployment-Anleitung](deployment.md). Ein selbst gehosteter Runner ist nicht erforderlich.
- **Eigene Agenten und eigene Infrastruktur:** Eigene Agenten dürfen denselben PR-Vertrag verwenden. CI kann auf dafür vorgesehenen eigenen lokalen Runnern laufen. Ein optionaler GitHub-Deploy-Button benötigt einen separaten lokalen Deployment-Runner; dieser führt keinen PR-Code aus und darf nur die feste Bridge mit `preview` oder `apply` anstoßen.

Der jeweilige CI-Runner erhält ausschließlich den Inhalt des Repositorys. Er parst die Home-Assistant-YAML-Dateien, sucht nach privaten Dateien, Laufzeitzuständen und wahrscheinlichen Zugangsdaten, führt die Pipeline-eigenen Tests genau einmal aus und wählt bei Bedarf eigene Vertragstests aus. Gitleaks prüft bei jedem Lauf den Arbeitsbaum; bei sicherheitsrelevanten Änderungen wird zusätzlich der vollständige Git-Verlauf geprüft. Alle Berechtigungen sind schreibgeschützt. Der CI-Runner hat weder einen Netzwerkweg noch Zugangsdaten zu Home Assistant.

Ein optionaler Desktop-Agent liegt vor GitHub in derselben Vertrauenszone wie der lokale Editor. Er darf ausschließlich einen Clone oder isolierten Worktree bearbeiten und einen Branch samt Pull Request vorbereiten. Er erhält weder `/config` noch Secrets, Home-Assistant-Zugang, Runner- oder Deployment-Rechte. Details stehen unter [Claude Desktop und Codex als lokale Bearbeitungsoberflächen](desktop-agents.md).

## Zwei Wege der Bereitstellung nach dem Merge

Beim Desktop-only-Pfad ruft ein vertrauenswürdiger Rechner im selben kontrollierten Netzwerk den geprüften Stand von `main` ab. Die zuständige Person prüft Commit und vollständiges Backup, vergleicht und kopiert nur die vorgesehenen Dateien und führt auf derselben Instanz die native Home-Assistant-Konfigurationsprüfung aus. Erst dann darf ein gezieltes Neuladen erfolgen. Der Rollback nutzt den von der Installation unterstützten Wiederherstellungsweg.

Im eigenen Infrastrukturmodell kann stattdessen ein manueller `workflow_dispatch` nach dem Merge den getrennten Deployment-Runner erreichen. Die Autorisierung bleibt lokal: feste Bridge, Modus `preview` oder `apply`, exakter `main`- und CI-SHA, exklusives Lock, wiederherstellbares Backup, native Prüfung und Rollback. Der Actions-Workspace ist nie die Quelle für das Deployment. Beide Endpfade sind manuell; keiner wird vom Pull-Request-Workflow oder Desktop-Agenten gestartet.

## Bedrohungsmodell

Ein Pull Request kann Workflows oder Skripte verändern. Sein Code ist daher nicht vertrauenswürdig. Verbinde normale Pull-Request-Workflows niemals mit einem weitreichend berechtigten selbst gehosteten Runner oder mit Home-Assistant-Zugangsdaten. Wer eigene CI-Runner nutzt, isoliert sie vom Deployment-Runner und vom Zielsystem. Eine erfolgreiche statische Prüfung sagt nichts darüber aus, ob installierte benutzerdefinierte Integrationen verfügbar sind, Geräte erreichbar sind, zeitliche Abläufe stimmen oder physische Sicherheit gewährleistet ist. Manuelles Review und eine Funktionskontrolle nach der Bereitstellung bleiben Pflicht.

## Risikobasierte Vertragstests

Die Testauswahl betrachtet die geänderten Zeilen und den zugehörigen obersten YAML-Block. Dort gefundene stabile IDs oder Entities werden mit den Dateien unter `tests/test_*.py` abgeglichen. So verbleiben anwendungsspezifische Verhaltenstests im eigenen Repository, während diese Vorlage allgemein nutzbar bleibt. Grundlegendes Parsen, Sicherheitsprüfungen, Pipeline-Unit-Tests und Gitleaks laufen immer.
