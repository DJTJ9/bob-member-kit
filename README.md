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
erzeugen", wird nur einmal angezeigt). Die Adzuna-/Jooble-Keys sind optional und
nur für `/bob:bob-scan` nötig.

Updates ziehst du mit `/plugin marketplace update bob-kit` — Auto-Update ist bei
Fremd-Marketplaces standardmäßig aus.

## Die zwei Befehle

| Befehl | Was er tut |
|---|---|
| `/bob:bob-score` | Holt wartende Jobs, extrahiert + bewertet sie mit DEINEM Claude, schreibt zurück |
| `/bob:bob-scan` | Sucht mit deinen eigenen (kostenlosen) Adzuna/Jooble-Keys neue Jobs und liefert sie ein |

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

**Welche Daten fließen:** Job-Rohtexte und deine Profil-Kriterien kommen vom
Server zu deinem Claude; Extraktionen und Scores gehen zurück. Deine Bewertungen
sind user-scoped — andere Member sehen sie nicht. Was der Server speichert, steht
im Datenschutz-Text auf der Website.

## Sicherheit

- Dein API-Token ist persönlich. Nicht teilen, nicht committen. Claude legt ihn im
  Schlüsselbund (macOS) bzw. in `~/.claude/.credentials.json` ab, nicht in diesem Repo.
- **Die Adzuna-/Jooble-Keys liegen im Klartext in `~/.claude/settings.json`.** Das ist
  ein bewusster Kompromiss: `/bob:bob-scan` muss sie direkt an die Such-APIs geben.
  Es sind kostenlose, rate-limitierte Keys ohne Zugriff auf Bob-Daten — aber leg dort
  nichts Wertvolleres ab.
- Stellenanzeigen-Rohtexte sind Fremdinhalte. Die Skills behandeln sie als Daten,
  niemals als Anweisungen.

## Lizenz

MIT — siehe [LICENSE](LICENSE).
