# Claude Desktop und Codex als lokale Bearbeitungsoberflächen

Claude Desktop und **Codex in der ChatGPT-Desktop-App** können Änderungen an einem lokalen Git-Checkout vorbereiten. Sie ersetzen weder CI noch die menschliche Prüfung und erhalten keinen Zugriff auf die laufende Home-Assistant-Installation. Sie passen sowohl zum Desktop-only-Modell ohne eigene Runner als auch zum Hybridmodell mit GitHub-gehosteter CI und optionalem lokalem Deployment-Runner. Im dritten Modell können stattdessen dauerhaft eigene Agenten und eigene lokale Runner verwendet werden.

Der gemeinsame verbindliche Weg reicht bis zum Merge; die drei Betriebsmodelle münden danach in zwei dokumentierte Endpfade:

```text
lokaler Clone → eigener Branch/Worktree → Diff und lokale Tests → Pull Request
→ GitHub CI → menschliche Prüfung → Merge nach main
├─ Desktop-only: kontrollierte manuelle lokale Bereitstellung gemäß deployment.md
├─ Hybrid: manueller workflow_dispatch → lokaler Deployment-Runner → feste Bridge
└─ eigene Agenten + eigene Runner: getrennte lokale CI-/Deployment-Rollen möglich
```

Im Desktop-only-Pfad läuft die mitgelieferte CI auf GitHub-gehosteten Runnern. Nach dem menschlichen Merge zieht eine zuständige Person `main` auf einem vertrauenswürdigen lokalen Rechner und folgt der manuellen Deployment-Checkliste. Dafür ist kein selbst gehosteter Runner nötig. Im Hybridpfad bleibt diese GitHub-gehostete CI bestehen; nur der optionale GitHub-Deploy-Button benötigt einen dedizierten lokalen Self-hosted Deployment-Runner. Ein dauerhaft eigener KI-Agent ist dafür nicht nötig. Ein GitHub-gehosteter Runner greift nie direkt auf Heimnetz oder Home Assistant zu.

> **Wichtig:** Öffne nur den lokalen Clone oder einen zugehörigen Worktree. Gib niemals `/config`, dein komplettes Home-Verzeichnis, eine SMB-Freigabe oder einen Ordner mit Zugangsdaten frei. Richte keine Home-Assistant-MCP-, Token-, SSH- oder automatische Deployment-Brücke für den Desktop-Agenten ein.

## Was ist was?

| Oberfläche | Geeignet für diesen Ablauf | Abgrenzung |
| --- | --- | --- |
| **Claude Desktop** | Lokale Dateien in einem bewusst verbundenen Projektordner lesen und bearbeiten, etwa über Cowork oder eine geprüfte Desktop Extension (lokaler MCP-Server) | Nicht mit **Claude Code** verwechseln. Claude Code ist ein separates agentisches Entwicklungswerkzeug mit eigener Terminal-/Desktop-Integration. Diese Seite beschreibt Claude Desktop. |
| **Codex in der ChatGPT-Desktop-App** | Einen lokalen Projektordner öffnen, Änderungen in einem isolierten Git-Worktree vorbereiten, Diff prüfen, testen, committen, pushen und einen PR anlegen | Nicht mit der **Codex CLI** verwechseln. Die CLI läuft im Terminal und hat eigene Startparameter. Diese Seite beschreibt die Desktop-App. |
| **GitHub Actions** | Unabhängige Prüfung des gepushten Branches und von `main`; im Desktop-only- und Hybridstandard auf GitHub-gehosteten Runnern, im Modell mit eigenen Agenten optional auf isolierten eigenen lokalen CI-Runnern | Kein Editor und kein Deployment-Agent. Die CI hat keinen Home-Assistant- oder Heimnetzzugriff. |
| **Bereitstellung** | Nach Review, grüner CI und Merge entweder kontrolliert manuell lokal oder optional per `workflow_dispatch` über einen getrennten lokalen Deployment-Runner | Darf nicht vom Desktop-Agenten automatisch ausgelöst oder umgangen werden. |

Beide Desktop-Oberflächen sind optional. Ein normaler Editor mit Git bleibt vollständig ausreichend.

## Gemeinsame Sicherheitsgrenzen

1. **Nur ein enger Arbeitsordner:** Verbinde ausschließlich den lokalen Clone oder einen eigens dafür angelegten Worktree. Keine übergeordneten Ordner und kein komplettes Benutzerverzeichnis.
2. **Keine Produktionsdateien:** `/config`, Home-Assistant-Samba-Freigaben und andere Live-Mounts bleiben außerhalb des freigegebenen Ordners. Ein Symlink aus dem Clone auf solche Ziele ist ebenfalls tabu.
3. **Keine Secrets:** `secrets.yaml`, `.env`, Home-Assistant-Token, SMB-Zugangsdaten, SSH-Schlüssel, Browserprofile und GitHub-Tokens dürfen weder im Projektordner liegen noch in einen Chat oder Prompt kopiert werden.
4. **Kein direkter `main`-Push:** Jede Änderung beginnt in einem eigenen Branch oder Worktree. `main` wird ausschließlich über einen geprüften Pull Request verändert.
5. **Begrenzte Rechte:** Verwende den normalen Sandbox-/Freigabemodus und bestätige Erweiterungen sowie zusätzliche Zugriffe bewusst. Keine Modi wie „Full access“, `danger-full-access`, „Skip all approvals“ oder andere Bypass-/Dangerous-Einstellungen.
6. **Keine Deployment-Werkzeuge:** Der Agent darf Diff, Tests, Commit und PR vorbereiten. Er darf keine Home-Assistant-API aufrufen, keine Dateien auf die Instanz kopieren und keinen Deployment-Workflow starten.
7. **Der Mensch bleibt Gate:** Lies den vollständigen Diff, prüfe unerwartete Dateien, führe die lokalen Tests selbst aus und kontrolliere den PR. Erst nach grüner GitHub-CI und menschlicher Freigabe wird gemergt.

Agentische Oberflächen können Anweisungen aus Dateien oder Webseiten übernehmen. Halte Web-, Connector- und Schreibzugriff deshalb so eng wie möglich und stoppe die Aufgabe bei unerwartetem Zugriff oder wachsendem Umfang.

## Vorbereitung des lokalen Clone

Die folgenden Befehle werden in einem normalen Terminal ausgeführt, nicht von Home Assistant:

```bash
git clone https://github.com/DEIN-NAME/DEIN-REPOSITORY.git
cd DEIN-REPOSITORY
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
git switch main
git pull --ff-only origin main
```

Unter Windows kann die Aktivierung und der Python-Aufruf je nach Installation anders heißen; die Repository-Prüfung selbst bleibt `./scripts/validate.sh --all` in einer Bash-Umgebung wie Git Bash oder WSL. Öffne anschließend **genau den Ordner `DEIN-REPOSITORY`**, nicht dessen Elternordner.

Prüfe vor dem Verbinden:

```bash
git status --short --branch
git remote -v
git check-ignore -v secrets.yaml
```

`secrets.yaml` muss ignoriert sein und darf nicht im Clone angelegt werden. Der Clone soll keine Live-Mounts oder Symlinks auf Home Assistant enthalten.

## Claude Desktop einrichten

### Installation auf macOS und Windows

1. Lade Claude Desktop ausschließlich über die [offizielle Download-Seite](https://claude.ai/download).
2. Anthropic nennt derzeit macOS 13 oder neuer und Windows 10 oder neuer als Mindestversionen.
3. Installiere die Anwendung, starte sie aus „Programme“ beziehungsweise dem Startmenü und melde dich an.
4. Halte Claude Desktop aktuell. Menübezeichnungen können sich ändern; Anthropic dokumentiert aktuell **Settings → Desktop app** und teilweise noch die ältere Ansicht **Settings → Extensions**.

### Engen Ordnerzugriff wählen

Für eine dateibasierte Aufgabe gibt es in Claude Desktop zwei getrennte Wege:

- **Cowork/verbundener Ordner:** Verbinde nur den lokalen Repository-Ordner für die konkrete Aufgabe. Anthropic weist darauf hin, dass aktuelle Cowork-Sitzungen in der Cloud laufen können und verbundene lokale Dateien über Claude Desktop erreichen; diese Dateien können dabei auf Anthropic-Systemen verarbeitet werden. Verbinde daher keine vertraulichen oder übergeordneten Ordner.
- **Desktop Extension (lokaler MCP-Server):** Nutze sie nur, wenn ein lokales Werkzeug wirklich erforderlich ist. Desktop Extensions laufen auf deinem Rechner mit deinen lokalen Benutzerrechten. Wähle möglichst eine von Anthropic geprüfte Erweiterung aus dem Verzeichnis, kontrolliere ihre angeforderten Rechte und konfiguriere als erlaubten Pfad ausschließlich den Clone. Installiere keine unbekannte `.mcpb`-Datei.

Der offizielle Weg zu Erweiterungen lautet derzeit **Settings → Desktop app → Manage neben Extensions → Browse extensions**. Unter **Advanced settings** lassen sich benutzerdefinierte `.mcpb`-Pakete installieren; für diesen Einsteigerablauf ist das nicht empfohlen. Den Verbindungsstatus und die Werkzeuge zeigt Claude Desktop über **+ → Connectors** oder im Bereich für lokale MCP-Server.

Ein Remote-Connector ist für lokale Dateien nicht die passende Wahl: Anthropic empfiehlt Desktop Extensions für Werkzeuge, die auf dem Rechner laufen oder Betriebssystemzugriff benötigen. Für diesen Workflow wird insbesondere **kein** Remote- oder lokaler Home-Assistant-Connector benötigt.

### Sicherer Ablauf mit Claude Desktop

1. Erstelle den Branch selbst im Terminal:

   ```bash
   git switch -c fix/kurze-beschreibung
   ```

2. Verbinde ausschließlich diesen Clone. Wähle manuelle Freigaben; erlaube keine allgemeine Computersteuerung, keinen Browserzugriff und keine weiteren Ordner.
3. Bitte Claude zuerst nur um Analyse und Plan. Erlaube danach gezielte Änderungen an den genannten YAML- und Testdateien.
4. Führe die Prüfung selbst im Terminal aus:

   ```bash
   ./scripts/validate.sh --all
   git status --short
   git diff --check
   git diff
   ```

5. Prüfe jede geänderte Datei. Committe und pushe erst danach. Claude darf eine PR-Beschreibung entwerfen, der Mensch öffnet beziehungsweise bestätigt den Pull Request.

Claude Desktop ist hier lediglich die Bearbeitungsoberfläche. Diese Anleitung aktiviert weder Claude Code noch dessen Berechtigungsmodi.

## Codex in der ChatGPT-Desktop-App einrichten

OpenAI bezeichnet die aktuelle Desktop-Oberfläche in der Dokumentation als **ChatGPT desktop app**; darin wird für Entwicklungsaufgaben **Codex** gewählt. Die Einführung erfolgte zunächst auf macOS, die Herstellerankündigung nennt inzwischen auch Windows. Verwende die [offizielle Download-Seite](https://chatgpt.com/download/) und die [aktuelle App-Dokumentation](https://developers.openai.com/codex/app), da Produkt- und UI-Namen sich ändern können.

### Lokales Projekt und Worktree

1. Installiere die App auf macOS oder Windows, starte sie und melde dich an.
2. Wähle in der App **Codex** und füge den lokalen Clone als Projektordner hinzu. Ein lokales Projekt kann Dateien in allen angehängten Ordnern lesen und ändern. Hänge deshalb nur den Clone an und keine zusätzlichen Ordner.
3. Lege `DEIN-REPOSITORY` als primären Ordner fest. Codex sucht dort automatisch nach `AGENTS.md` und verwendet ihn als Standard für Git-Aktionen.
4. Starte die Aufgabe bevorzugt mit **Work in: This computer** und **Worktree**. `Local` arbeitet direkt im aktuellen Checkout; `Worktree` isoliert Änderungen in einer zusätzlichen Git-Arbeitskopie. `Cloud` ist für diesen ausdrücklich lokalen Ablauf nicht erforderlich.
5. Behalte den normalen Sandbox-Modus mit Rückfragen bei. OpenAI dokumentiert `workspace-write` als begrenzten Standard für lokale Arbeit und `on-request` für Freigaben. Wähle nicht **Full access** beziehungsweise `danger-full-access` und keine Richtlinie, die Rückfragen vollständig abschaltet.

Codex-Worktrees starten standardmäßig mit einem losgelösten `HEAD`. Nach der Prüfung erzeugst du in der App über **Create branch here** einen Branch, zum Beispiel `fix/kurze-beschreibung`. Alternativ kannst du per **Hand off** kontrolliert in den lokalen Checkout wechseln. Versuche nicht, denselben Branch gleichzeitig im Worktree und im normalen Checkout auszuchecken.

> Füge `secrets.yaml`, `.env`, Schlüssel oder Zugangsdaten niemals zu `.worktreeinclude` hinzu. Sie würden sonst in verwaltete Worktrees kopiert. Dieses Template benötigt solche Dateien nicht für seine statischen Tests.

### `AGENTS.md` als dauerhafte Leitplanke

Dieses Template enthält eine `AGENTS.md` im Repository-Wurzelverzeichnis. Codex lädt solche Projektanweisungen automatisch. Sie begrenzen nicht technisch die Sandbox, halten aber den gewünschten Ablauf dauerhaft im Kontext. Die Sandbox- und GitHub-Regeln bleiben die wirksamen Gates.

### Sicherer Ablauf mit Codex

1. Starte einen neuen Codex-Chat im **Worktree**, ausgehend vom aktuellen `main`.
2. Gib eine eng begrenzte Aufgabe und nenne die erlaubten Dateien. Lass Codex den Diff und die Tests vorbereiten.
3. Prüfe den Diff in der App. Die App kann einzelne Abschnitte oder Dateien stagen beziehungsweise verwerfen, committen, einen Branch pushen und einen Pull Request erstellen. Diese Bedienfunktionen sind kein Ersatz für Review.
4. Führe im integrierten oder normalen Terminal aus:

   ```bash
   ./scripts/validate.sh --all
   git status --short
   git diff --check
   git diff origin/main...HEAD
   ```

5. Erzeuge einen benannten Branch, committe ausschließlich die erwarteten Dateien und öffne einen PR gegen `main`. Aktiviere keinen direkten Push nach `main` und keinen automatischen Merge.

Diese Anleitung konfiguriert nicht die Codex CLI. CLI-Schalter und Desktop-App-Modi sind nicht austauschbar.

## Prompt-Beispiele

### Home-Assistant-YAML ändern

```text
Arbeite ausschließlich in diesem lokalen Repository und nur in einem eigenen
Branch/Worktree. Ändere nur packages/flur.yaml und falls erforderlich einen
gezielten Test unter tests/. Lies zuerst AGENTS.md und die vorhandene Struktur.

Ziel: [gewünschtes Verhalten präzise beschreiben]. Behalte stabile IDs bei,
verwende keine echten Hostnamen, Entity-IDs mit Personenbezug oder Secrets.
Richte keinen Zugriff auf Home Assistant ein und führe kein Deployment aus.
Zeige mir zuerst den Plan. Führe danach ./scripts/validate.sh --all aus und
berichte echte Fehler, statt sie zu umgehen. Am Ende: geänderte Dateien,
Diff-Zusammenfassung, Testergebnis und offene manuelle HA-Prüfungen.
```

### Nur prüfen und testen

```text
Ändere noch keine Dateien. Prüfe den Diff gegen origin/main auf YAML-Fehler,
unbeabsichtigte Löschungen, Klartext-Secrets, private Daten und fehlende stabile
IDs. Führe ./scripts/validate.sh --all aus. Gib den exakten Befehl, Exit-Status
und eine kurze Fehleranalyse aus. Kein Netzwerkzugriff, kein Deployment und kein
Zugriff außerhalb dieses Repositorys.
```

### Pull Request vorbereiten

```text
Prüfe den vollständigen Diff gegen origin/main und entwirf eine deutsche
PR-Beschreibung mit: Zweck, geänderte Dateien, Risiko, ausgeführte lokale Tests,
manuelle Home-Assistant-Prüfung nach dem Deployment und Rollback. Erfinde keine
Testergebnisse. Pushe niemals direkt nach main, merge nicht und starte keinen
workflow_dispatch. Frage vor Push oder PR-Erstellung nach meiner Bestätigung.
```

## Übergang zu GitHub und Deployment

Nach der lokalen Agentenarbeit gelten dieselben Gates wie bei jeder anderen Änderung:

1. Der Branch wird gepusht und ein Pull Request gegen `main` geöffnet.
2. GitHub Actions führt den verpflichtenden Job **Vorlage und Home-Assistant-Konfiguration prüfen / validate** aus.
3. Ein Mensch prüft Diff, Testnachweise, Datenschutz und Rollback-Angaben. Fehler werden in demselben Branch behoben und erneut durch CI geprüft.
4. Erst bei grüner CI und abgeschlossener Prüfung wird nach `main` gemergt.
5. Das Deployment bleibt ein **separater manueller Schritt**. Desktop-only-Nutzer folgen vollständig [Manuelle lokale Bereitstellung und Rollback](deployment.md); dafür ist kein selbst gehosteter Runner nötig.
6. Im Hybridmodell darf optional ein [`workflow_dispatch` auf `main`](github-triggered-deployment.md) den getrennten lokalen Deployment-Runner und dessen feste Bridge anstoßen. Sichere Voreinstellung ist `preview`; `apply` erfordert die dort beschriebenen Freigaben. Die CI bleibt GitHub-gehostet.
7. Im Modell mit eigenen Agenten dürfen eigene lokale CI-Runner verwendet werden. Eigene CI-Runner und Deployment-Runner bleiben getrennt.
8. Der Desktop-Agent erhält weder Runner-Zugriff noch Zugriff auf Live-Mounts oder Credentials und keine Berechtigungen für Bridge, Deployment, Home Assistant, Reload, Restart oder Rollback.

## Fehlerbehebung

### Der Agent sieht zu viele Dateien

Stoppe die Aufgabe. Entferne alle verbundenen Ordner bis auf den Clone und starte einen neuen Chat. Prüfe Symlinks mit `git ls-files -s` und den Arbeitsbaum mit `git status --short`. Wurde ein vertraulicher Inhalt an einen Dienst übertragen, behandle betroffene Zugangsdaten als offengelegt und rotiere sie.

### Claude Desktop zeigt die Erweiterung nicht an

Aktualisiere und starte Claude Desktop neu. Prüfe unter **Settings → Desktop app → Extensions** Konfiguration, vorhandenen Pfad und Logs. Installiere nicht ersatzweise eine unbekannte Erweiterung. Für reine Bearbeitung kann ein bewusst verbundener Cowork-Ordner genügen.

### Codex kann im Worktree nicht testen

Prüfe, ob die Abhängigkeiten im Worktree installiert sind. Die Desktop-App unterstützt lokale Umgebungen mit plattformspezifischen Setup-Skripten und Aktionen. Speichere darin nur reproduzierbare Installations- und Testbefehle, keine Secrets. Alternativ führe `./scripts/validate.sh --all` im Worktree-Terminal aus; das Skript erstellt `.venv` selbst.

### Git meldet, der Branch sei bereits in einem Worktree ausgecheckt

Nutze in der App **Hand off** oder wechsle im Worktree auf einen anderen Branch. Git erlaubt denselben Branch nicht gleichzeitig in mehreren Worktrees. Lösche keinen Worktree, bevor Diff und Commits gesichert sind.

### Push oder PR-Erstellung verlangt Netzwerkfreigabe

Das ist erwartbar: Netzwerkzugriff liegt außerhalb der lokalen Dateigrenze. Prüfe Branch, Diff und Ziel-Repository und erteile höchstens die engste einmalige Freigabe. Du kannst Push und PR auch selbst im Terminal beziehungsweise auf GitHub ausführen.

### Die App schlägt Deployment oder Home-Assistant-Zugriff vor

Lehne ab. Entferne entsprechende Connectoren oder Werkzeuge und wiederhole die Grenzen im Prompt. Der korrekte Übergang des Desktop-Agenten endet beim PR. Nach dem Merge wählt der Mensch entweder die kontrollierte manuelle lokale Bereitstellung oder den optionalen manuellen GitHub-Trigger mit getrenntem Deployment-Runner.

## Offizielle Quellen

Stand der Prüfung: 20. November 2026. Hersteller können Verfügbarkeit, Plananforderungen und UI-Bezeichnungen ändern; prüfe vor der Einrichtung die verlinkten Primärquellen.

### Anthropic

- [Claude Desktop installieren](https://support.claude.com/en/articles/10065433-install-claude-desktop)
- [Lokale MCP-Server und Desktop Extensions](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Desktop Extensions oder Remote Connectors wählen](https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors)
- [Claude Cowork sicher verwenden](https://support.claude.com/en/articles/13364135-use-claude-cowork-safely)

### OpenAI

- [ChatGPT-Desktop-App mit Codex](https://developers.openai.com/codex/app)
- [Projekte und lokale Ordner](https://learn.chatgpt.com/docs/projects)
- [Local, Worktree und Cloud](https://learn.chatgpt.com/docs/environments/modes)
- [Lokale Umgebungen und Git-Funktionen](https://learn.chatgpt.com/docs/environments/local-environment)
- [Codex-Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Sandbox und Freigaben](https://learn.chatgpt.com/docs/sandboxing)
- [`AGENTS.md` für Projektanweisungen](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Ankündigung der Codex-App einschließlich Windows-Aktualisierung](https://openai.com/index/introducing-the-codex-app/)
