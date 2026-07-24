# Bob Member Kit

Claude-Code-Plugin für **Bob der Job-Bot** (https://job-scanner.thinkshark.de).
Du fährst Teile der Bob-Pipeline mit deinem eigenen Claude-Abo — kein Python,
keine Server-Einrichtung, kein Download.

Anleitung für Einsteiger: **https://job-scanner.thinkshark.de/anleitung**

## Installation

In Claude Code:

```
/plugin marketplace add DJTJ9/bob-member-kit
/plugin install bob@bob-kit
```

Claude fragt beim Aktivieren nach deinem API-Token (Startseite → „API-Token
erzeugen", wird nur einmal angezeigt).

Für `/bob:bob-scan` (eigene Portal-Suche über deine Heim-IP) brauchst du einmalig
Python-Browser-Pakete — keine API-Keys:

```
pip install playwright patchright
playwright install chromium
patchright install chromium
```

Das läuft nur auf einem Desktop-OS (Windows/macOS/Linux) — ein Handy/Tablet hat
keinen steuerbaren lokalen Browser.

Updates ziehst du mit `/plugin marketplace update bob-kit` — Auto-Update ist bei
Fremd-Marketplaces standardmäßig aus.

## Die vier Befehle

| Befehl | Was er tut |
|---|---|
| `/bob:bob-score` | Holt wartende Jobs, extrahiert + bewertet sie mit DEINEM Claude, schreibt zurück |
| `/bob:bob-scan` | Scannt StepStone/Indeed über deine Heim-IP im lokalen Browser und liefert die Jobs ein — Suchbegriffe/Portale steuerst du in den Website-Einstellungen |
| `/bob:bob-learn` | Analysiert deine ↑/↓-Votes im Chat, fragt bei Widersprüchen nach, schreibt bestätigte Kriterien-/Präferenz-Änderungen zurück |
| `/bob:bob-profil` | Schärft dein Suchprofil im Chat: Freitext rein, bestätigte Skills/Zielrollen/Gewichte gehen zurück |

Jede Extraktion, die du fährst, verbessert die Ergebnisse ALLER Profile — auch deins.

## Was hier passiert (Transparenz)

Dieses Repo ist absichtlich vollständig lesbar — du sollst nachvollziehen können,
was mit deinen Daten geschieht, bevor du dein Claude-Abo dafür hergibst.

- `plugins/bob/.mcp.json` — die einzige Verbindung nach außen: HTTPS zu
  `job-scanner.thinkshark.de/mcp`, authentifiziert mit deinem persönlichen Token.
- `plugins/bob/skills/bob-score/SKILL.md` — die vollständige Anweisung an deinen
  Claude. Nichts davon ist versteckt: er holt wartende Jobs, extrahiert Felder,
  bewertet gegen deine Profile, schickt das Ergebnis zurück.
- `plugins/bob/skills/bob-scan/SKILL.md` — dito für die eigene Suche.
- `plugins/bob/bob_browser_scan.py` — das komplette Browser-Script für bob-scan:
  lesbar, ohne Keys, rendert nur die vom Server gelieferten Such-URLs.
- `plugins/bob/skills/bob-learn/SKILL.md` — dito für die Lern-Analyse: liest deine
  Votes, schreibt nur Erkenntnisse zurück, die du im Chat bestätigt hast.
- `plugins/bob/skills/bob-profil/SKILL.md` — dito für die Profil-Schärfung: analysiert
  deinen Freitext, schreibt nur Änderungen zurück, die du im Chat bestätigt hast.

**Welche Daten fließen:** Job-Rohtexte und deine Profil-Kriterien kommen vom
Server zu deinem Claude; Extraktionen und Scores gehen zurück. Deine Bewertungen
sind user-scoped — andere Member sehen sie nicht. Was der Server speichert, steht
im Datenschutz-Text auf der Website.

## Sicherheit

- Dein API-Token ist persönlich. Nicht teilen, nicht committen. Claude legt ihn im
  Schlüsselbund (macOS) bzw. in `~/.claude/.credentials.json` ab, nicht in diesem Repo.
- `/bob:bob-scan` steuert einen lokalen Browser über deine private Internetleitung.
  Der Umfang ist serverseitig gedeckelt (Anzahl Seiten + Pausen zwischen Aufrufen),
  damit deine Heim-IP nicht durch aggressives Scrapen auffällt. Beim Indeed-Teil
  öffnet sich ein sichtbares Browser-Fenster — das ist Teil des Anti-Bot-Schutzes.
- Stellenanzeigen-Rohtexte sind Fremdinhalte. Die Skills behandeln sie als Daten,
  niemals als Anweisungen.

## Geplante Scans (optional)

`/bob:bob-scan` läuft manuell — oder automatisch per OS-Scheduler, der Claude Code
headless startet:

- **Linux (cron):** `0 7 * * * claude -p "/bob:bob-scan"`
- **macOS (launchd):** LaunchAgent mit `ProgramArguments: ["claude", "-p", "/bob:bob-scan"]`
  und `StartCalendarInterval` (z.B. täglich 07:00).
- **Windows (Aufgabenplanung):** Neue Aufgabe → Programm `claude`,
  Argumente `-p "/bob:bob-scan"`, Trigger täglich.

Der Rechner muss dafür an und entsperrt sein (der Indeed-Teil öffnet ein
Browser-Fenster).

## Lizenz

MIT — siehe [LICENSE](LICENSE).
