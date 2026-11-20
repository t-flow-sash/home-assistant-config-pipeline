# Manuelles GitHub-Deployment mit lokalem Vertrauensanker

Diese optionale Variante ist der Deployment-Teil des **Hybridmodells Desktop-Agent + GitHub Actions**: Ein Desktop-Agent bearbeitet Clone oder Worktree und öffnet einen PR, ein GitHub-gehosteter Runner validiert, ein Mensch merged und erst danach darf ein manueller **Deploy-Button in GitHub** einen kleinen lokalen Self-hosted Deployment-Runner erreichen. Ein dauerhaft eigener KI-Agent ist nicht nötig. GitHub löst den Vorgang nur aus. Welche geprüfte Version tatsächlich in Home Assistant geschrieben werden darf, entscheidet eine feste, lokal installierte Bridge im Heimnetz.

Dasselbe Deployment-Muster kann im Modell **eigene Agenten + eigene lokale Runner** verwendet werden; dort müssen lokaler CI-Runner und lokaler Deployment-Runner strikt getrennt bleiben. Für **Desktop-only ohne eigene Runner** bleibt stattdessen der [vollständige manuelle lokale Ablauf](deployment.md) maßgeblich.

> **Sichere Voreinstellung:** Beginne ausschließlich mit `preview`. Aktiviere `apply` erst, nachdem Vorschau, Rechte, Backup und Rollback ohne echte Änderung geprüft wurden. Weder `preview` noch `apply` laden Home Assistant neu oder starten es neu.

Dieses Repository veröffentlicht bewusst **keine generische schreibende Bridge**. Ein allgemeiner `copy`-, `rsync`-, `rm`- oder Shell-Writer könnte die Besonderheiten deiner Installation nicht sicher abbilden.

## Wann passt dieser Aufbau?

Er passt, wenn alle folgenden Punkte erfüllt sind:

- das abgeleitete Konfigurations-Repository ist privat;
- Änderungen gelangen nur per geprüftem Pull Request nach `main`;
- Home Assistant ist nur im Heimnetz erreichbar;
- ein dedizierter, selbst gehosteter Runner steht im Heimnetz bereit;
- du kannst eine kleine, installationsspezifische Bridge als `root` installieren und prüfen;
- Backup und Wiederherstellung sind bereits erprobt.

Wenn dir diese Begriffe noch nicht vertraut sind, bleibe beim [manuellen lokalen Ablauf](deployment.md). Der GitHub-Button ist Komfort, kein Ersatz für ein Wiederherstellungskonzept.

## Die drei Komponenten

```text
GitHub: manueller workflow_dispatch auf main
        │  Environment-Policy + preview/apply + erwarteter SHA
        ▼
selbst gehosteter Deployment-Runner im Heimnetz
        │  exakt erlaubtes sudo: feste Bridge, fester Modus
        ▼
lokale root-eigene Bridge
        ├─ ignoriert den Actions-Workspace
        ├─ übernimmt nur grünes origin/main
        ├─ sperrt parallele Deployments
        ├─ Vorschau → Backup → Apply → HA check_config
        └─ bei Fehler: Rollback → HA check_config
```

### 1. GitHub-Workflow: Auslöser, nicht Writer

Ein eigener Workflow wird nur über **Actions → Workflow auswählen → Run workflow** (`workflow_dispatch`) gestartet. Er:

- läuft ausschließlich für `refs/heads/main`;
- verwendet minimale Rechte (`contents: read`);
- deklariert ein geschütztes GitHub Environment;
- serialisiert Deployments mit einer nicht abbrechbaren Concurrency-Gruppe;
- fragt `preview` oder `apply` ab und verlangt für `apply` eine ausdrückliche Bestätigung;
- richtet **keinen Checkout** ein und führt keine Repository-Skripte aus;
- übergibt nur den erwarteten 40-stelligen Commit-SHA an eine feste lokale Bridge.

Der Workflow kopiert, löscht, lädt und startet nichts selbst.

### 2. Geschütztes Environment: äußere Freigabe

Lege unter **Settings → Environments** zum Beispiel ein Environment `home-assistant-production` an. Konfiguriere unter **Deployment branches and tags** eine Regel, die **exakt** den Branch `main` erlaubt. „All branches“ und bloße Namensmuster sind hierfür zu weit. Erlaube keine Tags.

Wenn dein GitHub-Tarif **Required reviewers** für Environments in privaten Repositorys anbietet, kannst du mindestens eine zweite Person als Freigabeinstanz eintragen und Selbstfreigabe ausschließen. Diese Funktion ist je nach Tarif und Repository-Sichtbarkeit nicht verfügbar. Behaupte dann nicht, ein Vier-Augen-Prinzip sei aktiv: Behalte die exakte `main`-Policy, den manuellen Trigger und die `apply`-Bestätigung bei.

Die Environment-Regel ist wichtig, aber nicht allein der Vertrauensanker. Workflow-YAML kann geändert werden. Die lokale Bridge muss deshalb sämtliche sicherheitsrelevanten Bedingungen selbst erneut prüfen.

### 3. Lokale root-eigene Bridge: Vertrauensanker

Die Bridge ist eine feste, installationsspezifische Datei außerhalb des Runner-Arbeitsverzeichnisses. Sie und ihre Konfiguration sind Eigentum von `root`, für den Runner nicht beschreibbar und über `sudoers` nur mit exakt zwei Befehlen erreichbar:

```text
/usr/local/sbin/ha-deploy-bridge preview
/usr/local/sbin/ha-deploy-bridge apply
```

Der erwartete Commit-SHA wird als genau eine Zeile über die Standardeingabe übergeben. Erlaubt werden weder eine Shell noch variable Skriptpfade, Kopierprogramme, Löschprogramme, freie Argumente, ein allgemeiner Rollback-Befehl oder `sudo` auf Repository-Dateien.

Die konkrete Implementierung bleibt in deinem privaten Betriebs-Repository. Vor der Installation muss sie auf deine Home-Assistant-Variante, Mounts, Eigentümer, Dateiliste, Backup-API und native Prüfart zugeschnitten werden.

## Verbindlicher Bridge-Vertrag

Eine Bridge ist erst akzeptabel, wenn sie alle folgenden Eigenschaften erzwingt.

### Quelle und Freigabe

- Sie ignoriert `$GITHUB_WORKSPACE` und jeden vom Workflow gelieferten Pfad.
- Sie arbeitet aus einem festen, root-eigenen, nicht vom Runner beschreibbaren Clone des **erwarteten Repositorys**.
- Sie prüft die exakte Origin-URL, einen sauberen Arbeitsbaum und deaktivierte Git-Hooks.
- Sie aktualisiert ausschließlich per Fast-forward auf `origin/main`; kein anderer Branch und kein Tag ist zulässig.
- `origin/main` muss exakt dem übergebenen SHA entsprechen.
- Für genau diesen SHA muss der festgelegte Validierungsworkflow als abgeschlossener, erfolgreicher **Push-Lauf auf `main`** nachweisbar sein. Ein grüner PR-Lauf, ein manueller Lauf oder ein anderer SHA genügt nicht.

### Lokale Ausführung

- Sie hält während des gesamten Vorgangs ein exklusives Lock in einem root-eigenen Verzeichnis; parallele Deployments brechen ab.
- `preview` zeigt nur die vorab erlaubten Änderungen und verändert weder Ziel noch Backup.
- `apply` akzeptiert ausschließlich eine feste Positivliste von Dateien und Zielen. Eine in Git fehlende Datei bedeutet nicht automatisch „löschen“.
- Vor der ersten Änderung erstellt und verifiziert sie ein vollständiges, wiederherstellbares Backup.
- Nach dem Schreiben führt sie die native Home-Assistant-Konfigurationsprüfung auf **derselben Instanz** aus.
- Schlägt diese Prüfung fehl, stellt sie den unmittelbar zuvor gesicherten Zustand wieder her und führt die native Prüfung erneut aus.
- Fehler beim Backup, Schreiben, Prüfen, Rollback oder erneuten Prüfen führen zu einem harten Fehlerstatus.
- Sie führt weder automatisch Reload noch Restart aus. Das ist ein späterer, getrennt freizugebender Bedienvorgang.

### Eigentum und Berechtigungen

- Bridge, Konfiguration, root-eigener Clone, Lock-Verzeichnis und lokale Zugangsdaten gehören `root` und sind für den Runner nicht schreibbar.
- Der Runner hat keine direkten Schreibrechte auf die Home-Assistant-Konfiguration und keinen allgemeinen `sudo`-Zugriff.
- `sudo -l -U <runner-benutzer>` zeigt nur die beiden festen Bridge-Aufrufe.
- Lokale Home-Assistant- oder GitHub-Zugangsdaten liegen in root-lesbaren lokalen Dateien, nicht im Repository und möglichst nicht in GitHub-Secrets.

## Prüffähiges Workflow-Skelett

Das folgende Skelett zeigt nur die schmale Schnittstelle. Ersetze Environment- und Runner-Label im **privaten** abgeleiteten Repository. Übernimm keine privaten Namen in diese öffentliche Vorlage.

```yaml
name: Home Assistant manuell bereitstellen

on:
  workflow_dispatch:
    inputs:
      mode:
        description: Nur Vorschau oder bewusst anwenden
        required: true
        type: choice
        options: [preview, apply]
        default: preview
      apply_confirmation:
        description: Für apply exakt DEPLOY eingeben
        required: false
        type: string

permissions:
  contents: read

concurrency:
  group: home-assistant-production
  cancel-in-progress: false

jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    environment: home-assistant-production
    runs-on: [self-hosted, Linux, X64, ha-deploy]
    timeout-minutes: 30
    steps:
      # Absichtlich kein actions/checkout und kein Repository-Skript.
      - name: Eingabe prüfen
        shell: bash
        env:
          MODE: ${{ inputs.mode }}
          CONFIRMATION: ${{ inputs.apply_confirmation }}
        run: |
          set -euo pipefail
          case "$MODE" in
            preview) ;;
            apply) test "$CONFIRMATION" = DEPLOY ;;
            *) exit 2 ;;
          esac

      - name: Lokale root-eigene Bridge aufrufen
        shell: bash
        env:
          MODE: ${{ inputs.mode }}
          EXPECTED_SHA: ${{ github.sha }}
        run: |
          set -euo pipefail
          case "$MODE" in
            preview)
              printf '%s\n' "$EXPECTED_SHA" |
                sudo -- /usr/local/sbin/ha-deploy-bridge preview
              ;;
            apply)
              printf '%s\n' "$EXPECTED_SHA" |
                sudo -- /usr/local/sbin/ha-deploy-bridge apply
              ;;
            *) exit 2 ;;
          esac
```

Die `if`-Bedingung ist nur zusätzliche Absicherung. Die externe Environment-Branch-Policy und die lokale SHA-/`origin/main`-/CI-Prüfung bleiben erforderlich. Lege für `sudoers` keine Wildcards an; verwende `NOPASSWD` nur für diese beiden exakten Befehle.

## Warum kein GitHub-gehosteter Runner direkt ins Heimnetz gehört

GitHub-gehostete Runner sind kurzlebige, fremd betriebene Maschinen. Um von dort Home Assistant zu erreichen, müsstest du dein Heimnetz öffnen, einen Tunnel oder VPN-Zugang bereitstellen und Zugangsdaten in den Workflow geben. Das vergrößert Angriffsfläche und Schadensradius unnötig.

Der lokale Runner baut seine GitHub-Verbindung ausgehend auf und benötigt keinen eingehenden Port. Trotzdem ist er **keine Sandbox**: Jeder Job, der auf seine Labels geroutet wird, führt Workflow-Code mit seinen Benutzerrechten aus. Deshalb gilt:

- Verwende einen dedizierten, Repository-gebundenen Deployment-Runner und ein eindeutiges Label.
- Führe darauf keine `pull_request`- oder `pull_request_target`-Jobs und keinen PR-Code aus.
- Nutze den GitHub-gehosteten Runner weiterhin für normale Validierung.
- Verwende den Deployment-Runner nicht als allgemeinen Build-Rechner und nicht als Home-Assistant-System.
- Gib ihm keine direkten Zielrechte; die enge root-eigene Bridge ist die Autorisierungsgrenze.

Ein Fork-PR ist als nicht vertrauenswürdige Codeausführung zu behandeln. Auch ein schreibgeschütztes `GITHUB_TOKEN`, zurückgehaltene Secrets oder eine manuelle Fork-Freigabe machen einen dauerhaften lokalen Runner nicht sicher. Erst nach Review und Merge läuft der manuelle Deployment-Workflow auf `main`.

## Einmalige Einrichtung

1. Schütze `main`: Pull Request verlangen, den Validierungscheck verpflichtend machen und direkte Pushes verhindern.
2. Erstelle das Environment mit einer exakten `main`-Deployment-Branch-Policy.
3. Richte einen dedizierten Repository-Runner mit dem zusätzlichen Label `ha-deploy` und ohne direkte Home-Assistant-Rechte ein.
4. Implementiere die private Bridge nach dem Vertrag oben. Prüfe sie unabhängig; veröffentliche keine generische Writer-Version.
5. Installiere Bridge und Konfiguration root-eigen und nicht durch den Runner beschreibbar.
6. Erlaube in `sudoers` ausschließlich die exakten Modi `preview` und `apply`; prüfe die Datei mit `visudo -cf`.
7. Ergänze den Workflow im privaten Repository per Pull Request. Prüfe besonders: kein Checkout, kein PR-Trigger, feste Labels, Environment und `main`-Guard.
8. Führe nach grünem Merge zuerst einen echten `preview`-Lauf vom Default-Branch aus.
9. Aktiviere `apply` erst nach erfolgreicher Abnahme und nur mit bewusstem Benutzerauftrag.

## Abnahme vor dem ersten `apply`

- [ ] `main` ist geschützt; der konkrete Validierungscheck ist verpflichtend.
- [ ] Das Environment erlaubt exakt `main` und keine Tags.
- [ ] Ein fehlender tariflicher Required Reviewer ist als Einschränkung dokumentiert.
- [ ] Der Deployment-Workflow hat nur `workflow_dispatch`, minimale Rechte und keinen Checkout.
- [ ] Der lokale Runner ist dediziert, Repository-gebunden und führt keine PR-Jobs aus.
- [ ] Bridge, Clone, Konfiguration und Lock sind root-eigen und nicht runner-schreibbar.
- [ ] `sudoers` parst fehlerfrei und erlaubt nur `preview` sowie `apply` über die feste Bridge.
- [ ] Ungültige Modi, SHAs, Branches, Origins und nicht passende CI-Läufe werden abgewiesen.
- [ ] Ein paralleler Lauf wird durch das lokale Lock abgewiesen.
- [ ] `preview` verändert nachweislich weder Ziel noch Backup.
- [ ] Backup und Wiederherstellung wurden außerhalb eines echten Deployments erprobt.
- [ ] Ein absichtlich ungültiger Testfall beweist `check_config` → Rollback → erneutes `check_config`.
- [ ] Ein manueller `preview`-Run auf dem aktuellen grünen `main`-SHA ist erfolgreich.
- [ ] Es gibt keinen automatischen Reload oder Restart.

## Nach jedem Lauf zurücklesen

Ein grüner Actions-Lauf beweist nur, dass der Job erfolgreich endete. Prüfe zusätzlich:

- Workflow-Run, Modus, Branch und exakten SHA;
- von der Bridge bestätigten `origin/main`- und CI-SHA;
- bei `apply`: Backup-Kennung, Ergebnis der nativen Prüfung und gegebenenfalls Rollback-Prüfung;
- unveränderten Zustand bei `preview`;
- Home-Assistant-Protokolle und betroffene Funktionen;
- weiterhin sauberen root-eigenen Deployment-Clone.

Reload oder Restart bleibt eine getrennte, bewusste Entscheidung nach erfolgreicher Prüfung und Read-back.
