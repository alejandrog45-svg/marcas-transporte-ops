from marcas_transporte_ops import analysis


def row(q, page, impr, pos, clicks=0):
    return {"keys": [q, page], "impressions": impr, "position": pos, "clicks": clicks, "ctr": 0}


def test_opportunities_filters_and_sorts():
    rows = [row("a", "/1", 500, 12), row("b", "/2", 900, 3), row("c", "/3", 60, 9), row("d", "/4", 10, 10)]
    out = analysis.find_opportunities(rows)
    assert [o["query"] for o in out] == ["a", "c"]


def test_seo_drop_alert_and_no_alert_on_small_base():
    assert analysis.seo_alerts({"clicks": 10, "impressions": 500}, {"clicks": 100, "impressions": 500})
    assert analysis.seo_alerts({"clicks": 0, "impressions": 0}, {"clicks": 5, "impressions": 10}) == []
    assert analysis.seo_alerts({"clicks": 90, "impressions": 500}, {"clicks": 100, "impressions": 500}) == []


def test_conversion_alert_only_with_traffic():
    zero = {"sessions": 200, "events": {"click_whatsapp": 0, "lead_submit": 0}}
    assert analysis.conversion_alerts(zero)
    assert analysis.conversion_alerts({"sessions": 10, "events": {"click_whatsapp": 0}}) == []
    assert analysis.conversion_alerts({"sessions": 200, "events": {"click_whatsapp": 3}}) == []


def test_audit_alerts_flag_errors_and_slow():
    audit = {"pages": [
        {"url": "u1", "status": 404, "seconds": 0.2, "issues": ["HTTP 404"]},
        {"url": "u2", "status": 200, "seconds": 5.0, "issues": []},
        {"url": "u3", "status": 200, "seconds": 0.5, "issues": []},
    ]}
    a = analysis.audit_alerts(audit)
    assert len(a) == 2 and "u1" in a[0] and "u2" in a[1]


def test_report_renders_sections():
    md = analysis.render_report(None, {"clicks": 3, "impressions": 9}, None, [], [])
    assert "Sin alertas" in md and "Clics: 3" in md


def test_ga4_sessions_come_from_sessions_metric_not_session_start_events():
    from marcas_transporte_ops import google_api
    ses = {"rows": [{"metricValues": [{"value": "120"}]}]}
    ev = {"rows": [{"dimensionValues": [{"value": "session_start"}], "metricValues": [{"value": "999"}]}]}
    out = google_api.ga4_parse(ses, ev)
    assert out["sessions"] == 120 and out["session_start_events"] == 999
