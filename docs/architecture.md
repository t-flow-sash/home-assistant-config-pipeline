# Architektur und Vertrauensgrenzen

## Weg eines Pull Requests

Der von GitHub gehostete Runner erhält ausschließlich den Inhalt des Repositorys. Er parst die Home-Assistant-YAML-Dateien, sucht nach privaten Dateien, Laufzeitzuständen und wahrscheinlichen Zugangsdaten, führt die Pipeline-eigenen Tests genau einmal aus und wählt bei Bedarf eigene Vertragstests aus. Gitleaks prüft bei jedem Lauf den Arbeitsbaum; bei sicherheitsrelevanten Änderungen wird zusätzlich der vollständige Git-Verlauf geprüft. Alle Berechtigungen sind schreibgeschützt. Der Runner hat weder einen Netzwerkweg noch Zugangsdaten zu Home Assistant.

Ein optionaler Desktop-Agent liegt vor GitHub in derselben Vertrauenszone wie der lokale Editor. Er darf ausschließlich einen Clone oder isolierten Worktree bearbeiten und einen Branch samt Pull Request vorbereiten. Er erhält weder `/config` noch Secrets, Home-Assistant-Zugang, Runner- oder Deployment-Rechte. Details stehen unter [Claude Desktop und Codex als lokale Bearbeitungsoberflächen](desktop-agents.md).

## Weg der Bereitstellung

Nur ein vertrauenswürdiger Rechner im selben kontrollierten Netzwerk wie Home Assistant ruft den geprüften Stand von `main` ab. Diese Vorlage enthält kein allgemeines Hilfsprogramm, das in die laufende Installation schreibt. Vor der Änderung prüft die zuständige Person den genauen Commit und ein wiederherstellbares vollständiges Backup. Danach vergleicht und kopiert sie ausschließlich die vorgesehenen Dateien und führt auf derselben Instanz die native Home-Assistant-Konfigurationsprüfung aus. Erst dann darf ein gezieltes Neuladen erfolgen. Ein Rollback wird manuell über den von der jeweiligen Installation unterstützten Wiederherstellungsweg ausgeführt.

## Bedrohungsmodell

Ein Pull Request kann Workflows oder Skripte verändern. Sein Code ist daher nicht vertrauenswürdig. Verbinde normale Pull-Request-Workflows niemals mit einem weitreichend berechtigten selbst gehosteten Runner oder mit Home-Assistant-Zugangsdaten. Eine erfolgreiche statische Prüfung sagt nichts darüber aus, ob installierte benutzerdefinierte Integrationen verfügbar sind, Geräte erreichbar sind, zeitliche Abläufe stimmen oder physische Sicherheit gewährleistet ist. Manuelles Review und eine Funktionskontrolle nach der Bereitstellung bleiben Pflicht.

## Risikobasierte Vertragstests

Die Testauswahl betrachtet die geänderten Zeilen und den zugehörigen obersten YAML-Block. Dort gefundene stabile IDs oder Entities werden mit den Dateien unter `tests/test_*.py` abgeglichen. So verbleiben anwendungsspezifische Verhaltenstests im eigenen Repository, während diese Vorlage allgemein nutzbar bleibt. Grundlegendes Parsen, Sicherheitsprüfungen, Pipeline-Unit-Tests und Gitleaks laufen immer.
