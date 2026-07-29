"""Test für die JSON-LD-JobPosting-Extraktion von company/location aus Detailseiten-HTML."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "plugins" / "bob"))
import bob_browser_scan as scan

_HTML = '''<html><head><script type="application/ld+json">
{"@type":"JobPosting","title":"Python Dev",
 "hiringOrganization":{"@type":"Organization","name":"Acme GmbH"},
 "jobLocation":{"@type":"Place","address":{"addressLocality":"Berlin"}}}
</script></head><body>...</body></html>'''


def test_parse_jsonld_company_location():
    company, location = scan.parse_jsonld_org_location(_HTML)
    assert company == "Acme GmbH"
    assert location == "Berlin"


def test_parse_jsonld_missing_returns_empty():
    company, location = scan.parse_jsonld_org_location("<html><body>no ld</body></html>")
    assert company == ""
    assert location == ""
