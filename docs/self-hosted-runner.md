# Optionaler selbst gehosteter Runner

Der mitgelieferte Validierungsworkflow verwendet bewusst `ubuntu-latest`. Das ist der sichere Standard für **Desktop-only ohne eigene Runner** und für **Hybrid Desktop-Agent + GitHub Actions**. Desktop-only benötigt gar keinen selbst gehosteten Runner. Im Hybridmodell ist nur der optionale Deployment-Runner lokal selbst gehostet; die CI bleibt GitHub-gehostet. Im Modell **eigene Agenten + eigene lokale Runner** dürfen dagegen sowohl CI als auch Deployment auf eigenen lokalen Runnern betrieben werden, solange die Rollen strikt getrennt sind.

Es gibt zwei deutlich verschiedene Rollen:

- **CI-Runner:** Im Desktop-only- und Hybridstandard kurzlebig und GitHub-gehostet. Nur im Modell mit eigenen Agenten darf er selbst gehostet sein, bleibt aber unprivilegiert, vom Zielsystem isoliert und ohne Home-Assistant-Zugang.
- **Deployment-Runner:** Nur für den optionalen GitHub-Deploy-Button erforderlich und immer vom CI-Runner getrennt. Er führt ausschließlich den manuellen Workflow auf grünem `main` aus und darf nur eine feste root-eigene Bridge mit `preview` oder `apply` aufrufen. Siehe [Manuelles GitHub-Deployment mit lokalem Vertrauensanker](github-triggered-deployment.md).

Wenn du den Validierungsworkflow auf eigene CI-Runner umstellst:

1. Öffne in GitHub **Settings → Actions → Runners → New self-hosted runner**. Übernimm die aktuellen Befehle direkt aus GitHub und nicht aus einer Dokumentation.
2. Verwende einen eigens dafür vorgesehenen, jederzeit ersetzbaren Rechner beziehungsweise ein unprivilegiertes Benutzerkonto und ein selbst gewähltes Repository-spezifisches Label.
3. Gewähre keinen Zugriff auf `/config`, Backups, SSH-Schlüssel, Home-Assistant-Token, LAN-Verwaltungsoberflächen oder andere Repositorys.
4. Ändere nach Prüfung des Bedrohungsmodells ausschließlich `runs-on`.
5. Lasse die festgeschriebenen Action-Versionen und sämtliche Tests unverändert.
6. Führe nicht vertrauenswürdige Pull Requests aus Forks niemals automatisch aus. Verlange eine ausdrückliche Freigabe und bevorzuge kurzlebige Runner.
7. Route mit CI-Labels niemals Jobs auf den Deployment-Runner; nutze getrennte Runner-Registrierungen, Benutzer und Arbeitsverzeichnisse.

Verwende das Home-Assistant-System niemals zugleich als allgemeinen Pull-Request-Runner. Workflow-Code kann beliebige Befehle mit den Rechten des Runner-Benutzers ausführen. Registrierungstoken für Runner dürfen weder eingecheckt noch in Issues oder Protokolle eingefügt werden.

GitHub-gehostete und Self-hosted Runner sind nicht austauschbar: Ein GitHub-gehosteter Runner erhält niemals einen direkten Pfad ins Heimnetz oder zu Home Assistant. Ein Self-hosted Deployment-Runner führt niemals Pull-Request-Code aus. Der Desktop-Agent erhält weder Runner-Zugang noch Live-Mount, Credentials oder Deployment-Berechtigungen.

## Zusätzliche Grenze für einen Deployment-Runner

Ein dauerhafter Runner im Heimnetz ist keine Sandbox. Repository-Bindung und ein eigenes Label steuern nur, wohin GitHub einen Job sendet; sie autorisieren keinen Schreibzugriff. Deshalb darf ein Deployment-Runner keine `pull_request`- oder `pull_request_target`-Workflows ausführen, keine direkten Zielrechte besitzen und keine Programme aus dem Actions-Workspace mit erhöhten Rechten starten.

Gib insbesondere niemals pauschal `sudo` für eine Shell, `cp`, `rm`, `rsync`, einen variablen Skriptpfad oder Repository-Dateien frei. Zulässig ist nur eine lokal installierte, root-eigene und für den Runner nicht beschreibbare Bridge mit exakt aufgezählten Befehlen. Die GitHub-Environment-Policy muss exakt `main` erlauben; tarifabhängige Required Reviewers sind eine zusätzliche Freigabe, ersetzen aber die lokale Prüfung nicht.
