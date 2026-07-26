#!/usr/bin/env python3
"""Bob Browser-Scan: rendert die vom Server (MCP-Tool get_scan_config) gebauten
Such-URLs über die residential IP dieses Rechners, extrahiert Detail-URLs per
Pattern, rendert jede Detailseite und schreibt JSONL-Listings für push_jobs.

Engines: StepStone → playwright (headless), Indeed → patchright (headful — der
einzige Weg durch Cloudflare-Turnstile). Keine API-Keys, keine URL-Logik hier:
der Server liefert fertige Targets + Caps, dieses Script ist ein dummer
Fetch+Extract-Loop.

Aufruf (macht der /bob:bob-scan-Skill):
    python bob_browser_scan.py --config scan_config.json --out listings.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

_TIMEOUT_MS = 45000
_SETTLE_MS = 1500       # nach domcontentloaded: JS-Nachlade-Puffer
_MIN_TEXT_CHARS = 200   # kürzer = leere/geblockte Seite, kein Listing
_MAX_RAW_CHARS = 8000   # Server-Deckel (push_jobs) — hier schon kappen


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href" and value:
                    self.hrefs.append(value)


def extract_detail_urls(html: str, base_url: str, pattern: str) -> list[str]:
    """Rein/netzfrei: alle <a href> gegen base_url auflösen, per Pattern filtern,
    Reihenfolge stabil, dedupliziert."""
    parser = _LinkParser()
    parser.feed(html or "")
    rx = re.compile(pattern)
    seen: set[str] = set()
    out: list[str] = []
    for href in parser.hrefs:
        url = urljoin(base_url, href)
        if rx.search(url) and url not in seen:
            seen.add(url)
            out.append(url)
    return out


def make_listing(url: str, portal: str, title: str, body_text: str) -> dict | None:
    """Rein/netzfrei: eine JSONL-Zeile im push_jobs-Schema — None bei leerer/
    geblockter Seite."""
    text = (body_text or "").strip()
    if len(text) < _MIN_TEXT_CHARS:
        return None
    return {"url": url, "portal": portal,
            "raw_text": text[:_MAX_RAW_CHARS], "title": (title or "").strip()}


def _sync_playwright(engine: str):
    """Lazy Import — Modul bleibt ohne Browser-Deps importierbar (Tests)."""
    if engine == "patchright":
        from patchright.sync_api import sync_playwright
    else:
        from playwright.sync_api import sync_playwright
    return sync_playwright


def scan_portal(engine: str, targets: list[dict], max_detail: int,
                throttle_ms: int, out) -> dict:
    """Ein Browser pro Portal: erst alle Such-URLs, dann bis zu max_detail
    Detailseiten — mit throttle_ms Pause zwischen allen Navigationen."""
    stats = {"searches": 0, "details": 0, "skipped": 0, "errors": 0}
    headless = engine != "patchright"  # Indeed braucht headful (Turnstile)
    sync_playwright = _sync_playwright(engine)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        detail_urls: list[str] = []
        seen: set[str] = set()
        for t in targets:
            try:
                page.goto(t["search_url"], timeout=_TIMEOUT_MS,
                          wait_until="domcontentloaded")
                page.wait_for_timeout(_SETTLE_MS)
                html = page.content()
            except Exception as e:  # noqa: BLE001 — Fetch-Fehler = Target überspringen
                print(f"WARN Suche {t['search_url']}: {e}", file=sys.stderr)
                stats["errors"] += 1
                continue
            stats["searches"] += 1
            for u in extract_detail_urls(html, t["search_url"],
                                         t["detail_url_pattern"]):
                if u not in seen:
                    seen.add(u)
                    detail_urls.append(u)
            time.sleep(throttle_ms / 1000)
        for url in detail_urls[:max_detail]:
            try:
                page.goto(url, timeout=_TIMEOUT_MS, wait_until="domcontentloaded")
                page.wait_for_timeout(_SETTLE_MS)
                listing = make_listing(url, targets[0]["portal"],
                                       page.title(), page.inner_text("body"))
            except Exception as e:  # noqa: BLE001
                print(f"WARN Detail {url}: {e}", file=sys.stderr)
                stats["errors"] += 1
                continue
            if listing is None:
                stats["skipped"] += 1
            else:
                out.write(json.dumps(listing, ensure_ascii=False) + "\n")
                stats["details"] += 1
            time.sleep(throttle_ms / 1000)
        browser.close()
    return stats


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass  # umgeleiteter Stream ohne reconfigure — ok
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, help="JSON-Datei: Output von get_scan_config")
    ap.add_argument("--out", required=True, help="JSONL-Ausgabedatei (push_jobs-Listings)")
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    targets = cfg.get("targets", [])
    caps = cfg.get("caps", {})
    max_detail = int(caps.get("max_detail", 20))
    throttle_ms = int(caps.get("throttle_ms", 2000))
    if not targets:
        print("Keine Targets — Portal-Auswahl leer oder kein Profil.", file=sys.stderr)
        return 1
    by_portal: dict[str, list[dict]] = {}
    for t in targets:
        by_portal.setdefault(t["portal"], []).append(t)
    total: dict[str, dict] = {}
    with open(args.out, "w", encoding="utf-8") as out:
        for portal, ts in by_portal.items():
            engine = ts[0].get("engine", "playwright")
            print(f"→ {portal} ({engine}, {len(ts)} Suchen, max {max_detail} Details)")
            total[portal] = scan_portal(engine, ts, max_detail, throttle_ms, out)
    print(json.dumps({"portals": total, "out": args.out}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
