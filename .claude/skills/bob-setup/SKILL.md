---
name: bob-setup
description: Einmalige Einrichtung des Bob-Member-Zugangs — MCP-Verbindung mit API-Token, optional eigene Adzuna/Jooble-Keys für /bob-scan.
---

# Bob-Setup

Führe den User durch die Einrichtung. Stelle Fragen einzeln und warte auf Antworten.

## Schritt 1: API-Token

Frage den User nach seinem API-Token. Falls er keins hat: er bekommt es auf
https://job-scanner.thinkshark.de → einloggen → Startseite → "API-Token erzeugen"
(Format: `bob_` + 48 Hex-Zeichen; wird nur einmalig angezeigt).

## Schritt 2: MCP-Server registrieren

Führe aus (Token einsetzen):

```
claude mcp add --transport http bob https://job-scanner.thinkshark.de/mcp --header "Authorization: Bearer <TOKEN>"
```

## Schritt 3: Verbindung testen

Rufe das MCP-Tool `get_my_profile` (Server `bob`) auf. Erwartung: JSON mit den
Profilen des Users. Bei 401: Token falsch kopiert — Schritt 1 wiederholen (neues
Token erzeugen, das alte ist dann ungültig).
Hinweis: Nach `claude mcp add` muss die Claude-Session ggf. neu gestartet werden,
damit der Server verfügbar ist — dann `/bob-setup` einfach erneut ausführen, es ist
idempotent.

## Schritt 4 (optional): Eigene Such-Keys für /bob-scan

Frage, ob der User auch selbst Jobs suchen will (`/bob-scan`). Falls ja:

- **Adzuna** (kostenlos): https://developer.adzuna.com → registrieren → App-ID + App-Key
- **Jooble** (kostenlos): https://jooble.org/api/about → Key beantragen

Schreibe die Keys in `bob-keys.json` im Kit-Ordner (liegt in .gitignore):

```json
{"adzuna_app_id": "...", "adzuna_app_key": "...", "jooble_key": "..."}
```

Fehlende Keys sind ok — dann steht nur `/bob-score` zur Verfügung.

## Abschluss

Sage dem User: Einrichtung fertig. `/bob-score` bewertet wartende Jobs,
`/bob-scan` (mit Keys) sucht neue.
