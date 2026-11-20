# Fehlerbehebung

## Keine Home-Assistant-YAML gefunden

Bei einer neuen Vorlage ist das zu erwarten. Füge deine eigene `configuration.yaml`, `automations.yaml`, Dateien unter `packages/` oder einen anderen unterstützten Pfad hinzu. Eine Beispielkonfiguration wird bewusst nicht mitgeliefert.

## Eingebundene Datei oder eingebundenes Verzeichnis fehlt

Der Parser löst Pfade aus `!include` relativ zu der Datei auf, in der sie stehen. Committe die eingebundene YAML-Datei, sofern sie keine vertraulichen Daten enthält, oder korrigiere den Pfad. Lege niemals eine unechte Secret-Datei an, nur damit CI erfolgreich durchläuft.

## Secret im Klartext zugewiesen

Verschiebe den Wert in die ignorierte Datei `secrets.yaml` auf dem Home-Assistant-System und binde ihn mit `!secret` ein. Bei einem Fehlalarm solltest du das Beispiel oder den Namen anpassen, statt die Prüfung pauschal abzuschalten.

## Gitleaks meldet einen Fund

Behandle den Fund als echt, bis das Gegenteil belegt ist. Sperre oder rotiere offengelegte Zugangsdaten zuerst. Ein späteres Löschen entfernt sie nicht aus dem Git-Verlauf. Nimm nur nachweisliche Fehlalarme über eine eng begrenzte und dokumentierte Allowlist aus.

## GitHub ist grün, aber Home Assistant lehnt die Konfiguration ab

CI versteht die üblichen YAML-Tags, kennt aber weder deine installierte Home-Assistant-Version noch deine Integrationen. Brich die Bereitstellung ab und führe `ha core check` auf der tatsächlichen Installation aus. Schlägt die Prüfung fehl, stelle das vor der Bereitstellung erstellte Backup wieder her.

## Wie stelle ich die Konfiguration bereit?

Es gibt bewusst kein allgemeines Hilfsprogramm, das in die laufende Installation schreibt. Folge der manuellen Checkliste unter `docs/deployment.md`: Bestätige den geprüften Stand von `main`, prüfe ein vollständiges Backup, vergleiche und kopiere ausschließlich die vorgesehenen Dateien und führe auf derselben Home-Assistant-Instanz die native Konfigurationsprüfung aus. Ersetze `/config` niemals gesammelt.

## Kein eigener gezielter Test wurde ausgewählt

Das ist bei einem neuen, unkritischen Bereich in Ordnung; die grundlegenden Prüfungen wurden trotzdem ausgeführt. Dokumentiere den manuellen Funktionstest im Pull Request. Ergänze einen gezielten Vertragstest, sobald eine stabile ID oder Entity wichtiges Verhalten absichern kann.
