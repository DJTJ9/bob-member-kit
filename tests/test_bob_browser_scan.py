"""Netzfreie Tests für die puren Teile des Browser-Scan-Scripts.
Brauchen KEIN playwright/patchright (lazy imports im Script)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugins" / "bob"))

from bob_browser_scan import extract_detail_urls, make_listing

HTML = """<html><body>
<a href="/stellenangebote--Unity-Dev--123-inline.html">Job</a>
<a href="https://www.stepstone.de/stellenangebote--AI-Dev--456-inline.html">Job2</a>
<a href="/stellenangebote--Unity-Dev--123-inline.html">Dupe</a>
<a href="/cmp/some-company">Firma</a>
</body></html>"""


def test_extract_resolves_relative_filters_and_dedups():
    urls = extract_detail_urls(HTML, "https://www.stepstone.de/jobs/x",
                               r"stepstone\.de/stellenangebote--")
    assert urls == [
        "https://www.stepstone.de/stellenangebote--Unity-Dev--123-inline.html",
        "https://www.stepstone.de/stellenangebote--AI-Dev--456-inline.html"]


def test_extract_empty_html_returns_empty():
    assert extract_detail_urls("", "https://x.de", r"y") == []


def test_make_listing_caps_raw_text_and_strips_title():
    listing = make_listing("https://x.de/j", "stepstone", " Titel ", "T" * 9000)
    assert listing["raw_text"] == "T" * 8000
    assert listing["title"] == "Titel"
    assert listing["portal"] == "stepstone"


def test_make_listing_rejects_short_or_blocked_pages():
    assert make_listing("https://x.de/j", "stepstone", "T", "zu kurz") is None
