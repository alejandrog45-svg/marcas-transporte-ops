from marcas_transporte_ops import audit

GOOD = """<html><head><title>Traslados Aeropuerto Santiago | UberTransfer</title>
<meta name="description" content="Traslados con tarifa fija.">
<link rel="canonical" href="https://ubertransfer.cl/">
<script type="application/ld+json">{"@type":"WebSite"}</script></head>
<body><h1>Traslados</h1><img src="a.jpg" alt="auto"></body></html>"""

BAD = """<html><head><title></title><script type="application/ld+json">{roto</script></head>
<body><h1>a</h1><h1>b</h1>""" + "<img src='x.jpg'>" * 12 + "</body></html>"


def test_analyze_good_page_has_no_issues():
    info = audit.analyze_html(GOOD)
    assert info["h1_count"] == 1 and info["images_no_alt"] == 0
    assert audit.issues_for("u", 200, 0.5, info) == []


def test_analyze_bad_page_reports_all_problems():
    info = audit.analyze_html(BAD)
    issues = audit.issues_for("u", 200, 4.2, info)
    text = " | ".join(issues)
    for expected in ("falta <title>", "falta meta description", "H1 = 2", "falta canonical",
                     "12 imágenes sin alt", "sin lazy-load", "JSON-LD inválido", "lenta"):
        assert expected in text


def test_http_error_short_circuits():
    assert audit.issues_for("u", 404, 0.1, None) == ["HTTP 404"]
    assert audit.issues_for("u", 0, 0.1, None) == ["HTTP sin respuesta"]


def test_parse_sitemap_index_and_urlset():
    idx = ('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           "<sitemap><loc>https://x/p.xml</loc></sitemap></sitemapindex>")
    assert audit.parse_sitemap(idx) == (["https://x/p.xml"], [])
    urls = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://x/a/</loc></url></urlset>")
    assert audit.parse_sitemap(urls) == ([], ["https://x/a/"])


class _Resp:
    def __init__(self, status, text=""):
        self.status_code, self.text = status, text


class _Sess:
    def __init__(self, routes):
        self.routes = routes

    def get(self, url, **kw):
        r = self.routes.get(url)
        if isinstance(r, Exception):
            raise r
        return r or _Resp(404)


def test_audit_fails_explicitly_when_no_urls_discovered():
    import pytest
    import requests
    s = _Sess({"https://x/robots.txt": requests.ConnectionError("caído")})
    with pytest.raises(audit.AuditError):
        audit.run("https://x", s)


def test_discovery_report_records_robots_and_sitemap_status():
    rep = {}
    s = _Sess({"https://x/robots.txt": _Resp(200, "Sitemap: https://x/s.xml"),
               "https://x/s.xml": _Resp(200, '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x/a/</loc></url></urlset>')})
    assert audit.collect_urls("https://x", s, report=rep) == ["https://x/a/"]
    assert rep["robots"] == 200 and rep["sitemaps"][0]["urls"] == 1


class _FakeResp:
    def __init__(self, text, status=200):
        self.text, self.status_code = text, status


class _FakeSess:
    def __init__(self):
        self.calls = []

    def get(self, url, **kw):
        self.calls.append(url)
        if url.endswith("/robots.txt"):
            return _FakeResp("Sitemap: https://x.cl/sm.xml")
        if url.endswith("/sm.xml"):
            return _FakeResp('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                         "<url><loc>https://x.cl/a/</loc></url><url><loc>https://x.cl/b/</loc></url><url><loc>https://x.cl/c/</loc></url></urlset>")
        return _FakeResp(GOOD)


def test_run_respects_delay_and_max_urls(monkeypatch):
    pausas = []
    monkeypatch.setattr(audit.time, "sleep", lambda s: pausas.append(s))
    s = _FakeSess()
    res = audit.run("https://x.cl", session=s, delay=3, max_urls=2)
    assert [p["url"] for p in res["pages"]] == ["https://x.cl/a/", "https://x.cl/b/"]   # tope de 2 páginas
    assert pausas == [3]                                                                   # una pausa entre las dos
    assert not any(u.endswith("/c/") for u in s.calls)                                     # la tercera nunca se pide


def test_cli_audit_with_tag_writes_separate_files(tmp_path, monkeypatch):
    from marcas_transporte_ops import cli, config
    monkeypatch.setattr(cli, "DATA", tmp_path / "data")
    monkeypatch.setattr(cli, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(cli.audit, "run", lambda url, delay=0, max_urls=0: {"site": url, "pages": [], "generated": "2026-09-30T00:00:00Z"})
    cfg = config.Config(site_url="https://aereostar.cl", gsc_site="", ga4_property_id="", google_sa_json="", audit_tag="aereostar")
    assert cli.cmd_audit(cfg) == 0
    assert (tmp_path / "data" / "audit_aereostar_latest.json").exists()
    assert (tmp_path / "reports" / "audit_aereostar_latest.md").read_text(encoding="utf-8").startswith("# Informe Aereostar")
    assert not (tmp_path / "data" / "audit_latest.json").exists()

