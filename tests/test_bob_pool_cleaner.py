"""Netzfreie Tests für die puren Teile des Pool-Cleaner-Scripts.
Brauchen KEIN playwright/patchright (lazy imports im Script)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugins" / "bob"))

from bob_pool_cleaner import classify, engine_for

D = "https://indeed.com/viewjob?jk=1"


def test_classify_gone_on_404():
    assert classify(D, {"status": 404, "final_url": D, "text": ""}) == "gone"


def test_classify_gone_on_marker():
    r = {"status": 200, "final_url": D, "text": "Diese Stelle ist nicht mehr verfügbar."}
    assert classify(D, r) == "gone"


def test_classify_gone_on_redirect():
    r = {"status": 200, "final_url": "https://indeed.com/jobs", "text": "irgendwas"}
    assert classify(D, r) == "gone"


def test_classify_alive_on_content():
    r = {"status": 200, "final_url": D, "text": "Aufgaben und Anforderungen: Vollzeit"}
    assert classify(D, r) == "alive"


def test_classify_unclear_on_none_and_thin():
    assert classify(D, None) == "unclear"
    assert classify(D, {"status": 200, "final_url": D, "text": "leer"}) == "unclear"


def test_engine_for_indeed_is_patchright_else_playwright():
    assert engine_for("https://de.indeed.com/viewjob?jk=1") == "patchright"
    assert engine_for("https://www.stepstone.de/stellenangebote--x.html") == "playwright"
    assert engine_for("https://www.adzuna.de/details/123") == "playwright"
