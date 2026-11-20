# Optionaler selbst gehosteter Runner

Der mitgelieferte Workflow verwendet bewusst `ubuntu-latest`. Für Einsteiger ist das die sicherste Voreinstellung. Ein selbst gehosteter Runner ist optional und für die lokale Bereitstellung **nicht** erforderlich.

Wenn du dennoch umstellst:

1. Öffne in GitHub **Settings → Actions → Runners → New self-hosted runner**. Übernimm die aktuellen Befehle direkt aus GitHub und nicht aus einer Dokumentation.
2. Verwende einen eigens dafür vorgesehenen, jederzeit ersetzbaren Rechner beziehungsweise ein unprivilegiertes Benutzerkonto und ein selbst gewähltes Repository-spezifisches Label.
3. Gewähre keinen Zugriff auf `/config`, Backups, SSH-Schlüssel, Home-Assistant-Token, LAN-Verwaltungsoberflächen oder andere Repositorys.
4. Ändere nach Prüfung des Bedrohungsmodells ausschließlich `runs-on`.
5. Lasse die festgeschriebenen Action-Versionen und sämtliche Tests unverändert.
6. Führe nicht vertrauenswürdige Pull Requests aus Forks niemals automatisch aus. Verlange eine ausdrückliche Freigabe und bevorzuge kurzlebige Runner.

Verwende das Home-Assistant-System niemals zugleich als allgemeinen Pull-Request-Runner. Workflow-Code kann beliebige Befehle mit den Rechten des Runner-Benutzers ausführen. Registrierungstoken für Runner dürfen weder eingecheckt noch in Issues oder Protokolle eingefügt werden.
