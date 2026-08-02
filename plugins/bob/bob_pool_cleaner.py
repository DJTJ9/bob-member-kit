#!/usr/bin/env python3
"""Bob Pool-Cleaner: prüft Job-Verfügbarkeit über die Heim-Residential-IP dieses
Rechners (umgeht Portal-403). Liest candidates.json (Output des MCP-Tools
pull_availability_candidates), rendert jede URL lokal (playwright headless /
patchright headful für Block-Portale), klassifiziert mit einer PORTABLEN Kopie
von jobscanner.availability.classify und schreibt verdicts.jsonl
({fingerprint, verdict}) für push_availability_verdicts.

classify() + die Marker-Konstanten sind eine bewusste Kopie aus
jobscanner/availability.py — der Server bleibt maßgeblich, Drift wird manuell
gehalten. Einziger Unterschied: hier kommt bereits bereinigter Text
(page.inner_text) statt HTML herein → kein bs4 nötig; die Logik ist identisch.

Nicht-interaktiv/Cron-tauglich. Aufruf (macht der /bob:bob-pool-cleaner-Skill):
    python bob_pool_cleaner.py --candidates candidates.json --out verdicts.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

_TIMEOUT_MS = 45000
_SETTLE_MS = 1500
_THROTTLE_MS = 2000
_BLOCK_HOSTS = ("indeed.",)  # brauchen patchright headful (Cloudflare-Turnstile)

# --- Kopie aus jobscanner/availability.py (Server maßgeblich, Drift akzeptiert) ---
_GONE_MARKERS = (
    "nicht mehr verfügbar", "nicht mehr verfuegbar", "stelle wurde besetzt",
    "anzeige nicht gefunden", "diese stellenanzeige ist nicht mehr",
    "stellenanzeige nicht gefunden", "position has been filled",
    "job no longer available", "this job is no longer",
)
_CONTENT_KEYWORDS = (
    "anforderungen", "aufgaben", "ihr profil", "wir bieten", "bewerbung", "bewerben",
    "vollzeit", "teilzeit", "requirements", "responsibilities", "apply",
)
_MIN_CONTENT_HITS = 2


def classify(detail_url: str, rendered: dict | None) -> str:
    """gone (eindeutiges Weg-Signal), alive (Status 200 + Job-Inhalt), unclear (sonst).
    rendered erwartet {status, final_url, text} — text ist bereits bereinigt."""
    if rendered is None:
        return "unclear"
    status = rendered.get("status", 0)
    if status in (404, 410):
        return "gone"
    norm = (rendered.get("text", "") or "").lower()
    if any(marker in norm for marker in _GONE_MARKERS):
        return "gone"
    final_path = urlparse(rendered.get("final_url", "")).path.rstrip("/")
    detail_path = urlparse(detail_url).path.rstrip("/")
    if final_path and detail_path and final_path != detail_path:
        return "gone"
    if status == 200:
        hits = sum(1 for kw in _CONTENT_KEYWORDS if kw in norm)
        if hits >= _MIN_CONTENT_HITS:
            return "alive"
    return "unclear"
# --- Ende Kopie ---


def engine_for(url: str) -> str:
    """Block-Portale (Indeed) brauchen patchright headful, alle anderen playwright."""
    host = urlparse(url).netloc.lower()
    return "patchright" if any(b in host for b in _BLOCK_HOSTS) else "playwright"


def _sync_playwright(engine: str):
    """Lazy Import — Modul bleibt ohne Browser-Deps importierbar (Tests)."""
    if engine == "patchright":
        from patchright.sync_api import sync_playwright
    else:
        from playwright.sync_api import sync_playwright
    return sync_playwright


def render(url: str) -> dict | None:
    """Rendert url über die Heim-IP; gibt {status, final_url, text} oder None."""
    engine = engine_for(url)
    headless = engine != "patchright"
    sync_playwright = _sync_playwright(engine)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            resp = page.goto(url, timeout=_TIMEOUT_MS, wait_until="domcontentloaded")
            page.wait_for_timeout(_SETTLE_MS)
            rendered = {"status": resp.status if resp is not None else 0,
                        "final_url": page.url, "text": page.inner_text("body")}
            browser.close()
            return rendered
    except Exception as e:  # noqa: BLE001 — Render-Fehler = unclear, nicht abbrechen
        print(f"WARN render {url}: {e}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", required=True, help="JSON: Output von pull_availability_candidates")
    ap.add_argument("--out", required=True, help="JSONL-Ausgabe ({fingerprint, verdict})")
    args = ap.parse_args()
    cfg = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    candidates = cfg.get("candidates", [])
    if not candidates:
        print("Keine Kandidaten — nichts zu prüfen.", file=sys.stderr)
        return 1
    stats = {"gone": 0, "alive": 0, "unclear": 0}
    with open(args.out, "w", encoding="utf-8") as out:
        for c in candidates:
            fp, url = c.get("fingerprint"), c.get("url")
            if not (fp and url):
                continue
            verdict = classify(url, render(url))
            stats[verdict] += 1
            out.write(json.dumps({"fingerprint": fp, "verdict": verdict},
                                 ensure_ascii=False) + "\n")
            time.sleep(_THROTTLE_MS / 1000)
    print(json.dumps({"checked": sum(stats.values()), **stats, "out": args.out},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
