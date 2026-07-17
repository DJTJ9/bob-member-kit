# Bob Member Kit

Du fährst Teile der Bob-Pipeline (job-scanner.thinkshark.de) mit deinem eigenen
Claude-Abo. Kein Python, keine Server-Einrichtung — nur Claude Code + dieses Kit.

## Voraussetzungen

- Ein Claude-Abo (Pro reicht)
- Windows, macOS oder Linux

## Einrichtung (Windows)

1. **Claude Code installieren:** PowerShell öffnen und ausführen:
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
   (Alternativ mit Node.js: `npm install -g @anthropic-ai/claude-code`)
2. **Dieses Kit herunterladen** (Zip aus Discord) und entpacken, z.B. nach
   `C:\bob-member-kit`.
3. **Terminal im Kit-Ordner öffnen** (im Explorer: Rechtsklick → "Im Terminal öffnen")
   und `claude` starten.
4. **`/bob-setup` eingeben** und den Anweisungen folgen. Du brauchst dafür dein
   persönliches API-Token: auf https://job-scanner.thinkshark.de einloggen →
   Startseite → "API-Token erzeugen" (wird nur einmal angezeigt!).

## Die drei Befehle

| Befehl | Was er tut |
|---|---|
| `/bob-setup` | Einmalig: verbindet dein Claude mit Bob (MCP + Token), optional eigene Such-API-Keys |
| `/bob-score` | Holt wartende Jobs, extrahiert + bewertet sie mit DEINEM Claude, schreibt zurück |
| `/bob-scan` | Sucht mit deinen eigenen (kostenlosen) Adzuna/Jooble-Keys neue Jobs und liefert sie ein |

Jede Extraktion, die du fährst, verbessert die Ergebnisse ALLER Profile — auch deins.

## Sicherheit

- Dein API-Token ist persönlich. Nicht teilen, nicht committen.
- Stellenanzeigen-Rohtexte sind Fremdinhalte. Die Skills behandeln sie als Daten,
  niemals als Anweisungen.
