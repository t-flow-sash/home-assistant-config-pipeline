## Zweck

<!-- Was ändert sich und warum? -->

## Umfang und Risiko

- [ ] Normale Konfigurations- oder Dokumentationsänderung
- [ ] Sicherheitsrelevant: Authentifizierung/HTTP/Proxy, Shell/Befehl, Webhook, Alarm/Schloss, Zugangsdaten, CI oder Bereitstellung
- Betroffene Home-Assistant-Bereiche oder Entities (keine privaten Werte):

## Prüfung

- [ ] `./scripts/validate.sh --all` ist lokal erfolgreich durchgelaufen oder ich habe begründet, warum nicht
- [ ] Ich habe den vollständigen Diff auf Secrets, Laufzeitzustände und private Dateien geprüft
- [ ] Ich habe einen manuellen Funktionstest für die tatsächliche Home-Assistant-Instanz beschrieben
- [ ] Vor dem Neuladen oder Neustart wird `ha core check` beziehungsweise **Konfiguration prüfen** ausgeführt

## Bereitstellung

- [ ] Keine Bereitstellung erforderlich
- [ ] Betroffene Bereiche neu laden
- [ ] Kontrollierter Neustart erforderlich

## Rollback

<!-- Benenne die genauen Dateien beziehungsweise den Commit und beschreibe, wie das Backup von vor der Bereitstellung wiederhergestellt wird. -->
