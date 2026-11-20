# Optionaler selbst gehosteter Runner

Der mitgelieferte Validierungsworkflow verwendet bewusst `ubuntu-latest`. Für Einsteiger ist das die sicherste Voreinstellung. Ein selbst gehosteter Runner ist für die rein manuelle lokale Bereitstellung **nicht** erforderlich.

Es gibt zwei deutlich verschiedene Rollen:

- **Validierung:** Bleibt vorzugsweise auf dem kurzlebigen GitHub-gehosteten Runner, der keinen Zugang zum Heimnetz benötigt.
- **Manuell ausgelöstes Deployment:** Kann optional einen dedizierten lokalen Runner verwenden. Dieser führt ausschließlich den Workflow auf grünem `main` aus und darf nur eine feste root-eigene Bridge mit `preview` oder `apply` aufrufen. Siehe [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](github-triggered-deployment.md).

Wenn du dennoch umstellst:

1. Öffne in GitHub **Settings → Actions → Runners → New self-hosted runner**. Übernimm die aktuellen Befehle direkt aus GitHub und nicht aus einer Dokumentation.
2. Verwende einen eigens dafür vorgesehenen, jederzeit ersetzbaren Rechner beziehungsweise ein unprivilegiertes Benutzerkonto und ein selbst gewähltes Repository-spezifisches Label.
3. Gewähre keinen Zugriff auf `/config`, Backups, SSH-Schlüssel, Home-Assistant-Token, LAN-Verwaltungsoberflächen oder andere Repositorys.
4. Ändere nach Prüfung des Bedrohungsmodells ausschließlich `runs-on`.
5. Lasse die festgeschriebenen Action-Versionen und sämtliche Tests unverändert.
6. Führe nicht vertrauenswürdige Pull Requests aus Forks niemals automatisch aus. Verlange eine ausdrückliche Freigabe und bevorzuge kurzlebige Runner.

Verwende das Home-Assistant-System niemals zugleich als allgemeinen Pull-Request-Runner. Workflow-Code kann beliebige Befehle mit den Rechten des Runner-Benutzers ausführen. Registrierungstoken für Runner dürfen weder eingecheckt noch in Issues oder Protokolle eingefügt werden.

## Zusätzliche Grenze für einen Deployment-Runner

Ein dauerhafter Runner im Heimnetz ist keine Sandbox. Repository-Bindung und ein eigenes Label steuern nur, wohin GitHub einen Job sendet; sie autorisieren keinen Schreibzugriff. Deshalb darf ein Deployment-Runner keine `pull_request`- oder `pull_request_target`-Workflows ausführen, keine direkten Zielrechte besitzen und keine Programme aus dem Actions-Workspace mit erhöhten Rechten starten.

Gib insbesondere niemals pauschal `sudo` für eine Shell, `cp`, `rm`, `rsync`, einen variablen Skriptpfad oder Repository-Dateien frei. Zulässig ist nur eine lokal installierte, root-eigene und für den Runner nicht beschreibbare Bridge mit exakt aufgezählten Befehlen. Die GitHub-Environment-Policy muss exakt `main` erlauben; tarifabhängige Required Reviewers sind eine zusätzliche Freigabe, ersetzen aber die lokale Prüfung nicht.
