import json
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "panel" / "sync_google_ads.py"
SPEC = importlib.util.spec_from_file_location("sync_google_ads", MODULE_PATH)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
normalize, query, dates = sync.normalize, sync.query, sync.dates


def test_query_is_report_only():
    sql = query("2026-10-08", "2026-10-08")
    assert "metrics.clicks" in sql
    assert "message_chats" not in sql
    assert all(word not in sql.upper() for word in ("MUTATE", "UPDATE", "REMOVE"))


def test_default_dates_include_yesterday_and_today(monkeypatch):
    monkeypatch.delenv("GOOGLE_ADS_DATE", raising=False)
    monkeypatch.delenv("GOOGLE_ADS_DATE_FROM", raising=False)
    monkeypatch.delenv("GOOGLE_ADS_DATE_TO", raising=False)
    start, end = dates()
    assert end > start


def test_normalize_keeps_one_snapshot_per_day_and_replaces_returned_days(tmp_path, monkeypatch):
    output = tmp_path / "google_ads.json"
    output.write_text(json.dumps({
        "metrics": {"impressions": 10, "clicks": 1, "costClp": 100, "conversions": 0},
        "history": [{"dateFrom": "2026-10-07", "dateTo": "2026-10-07", "impressions": 10,
                     "clicks": 1, "costClp": 100, "conversions": 0}],
    }), encoding="utf-8")
    monkeypatch.setattr(sync, "OUT", output)
    rows = [
        {"campaign": {"id": "123", "name": "Campaign #1", "status": "ENABLED"},
         "segments": {"date": "2026-10-08"},
         "metrics": {"impressions": "794", "clicks": "52", "costMicros": "15068000000", "conversions": 0}},
        {"campaign": {"id": "123", "name": "Campaign #1", "status": "ENABLED"},
         "segments": {"date": "2026-10-09"},
         "metrics": {"impressions": "250", "clicks": "7", "costMicros": "2000000000", "conversions": 0}},
    ]
    result = normalize(rows, "2026-10-08", "2026-10-09")
    assert [(x["dateFrom"], x["clicks"]) for x in result["history"]] == [
        ("2026-10-07", 1), ("2026-10-08", 52), ("2026-10-09", 7)
    ]
    assert result["metrics"]["dateFrom"] == "2026-10-09"
    assert result["metrics"]["clicks"] == 7
    # "Última fecha" debe ser el último día con datos, no el inicio de la consulta.
    assert result["campaignHistory"][0]["lastSeen"] == "2026-10-09"


def test_normalize_keeps_real_totals_and_history(tmp_path, monkeypatch):
    output = tmp_path / "google_ads.json"
    output.write_text(json.dumps({"observed": {"clicks": 36}, "mode": "read_only"}), encoding="utf-8")
    monkeypatch.setattr(sync, "OUT", output)
    result = normalize([{
        "campaign": {"id": "123", "name": "Campaign #1", "status": "ENABLED"},
        "segments": {"date": "2026-10-08"},
        "metrics": {"impressions": "479", "clicks": "36", "costMicros": "11878000000", "ctr": 0.075, "conversions": 0},
    }], "2026-10-08", "2026-10-08")
    assert result["status"] == "connected"
    assert result["metrics"]["costClp"] == 11878
    assert result["metrics"]["clicks"] == 36
    assert result["history"][0]["dateFrom"] == "2026-10-08"
    assert "observed" not in result


def test_normalize_does_not_replace_stopped_campaign_with_zeroes(tmp_path, monkeypatch):
    output = tmp_path / "google_ads.json"
    output.write_text(json.dumps({
        "campaignIds": ["123"], "campaignNames": ["Campaña detenida"],
        "metrics": {"impressions": 479, "clicks": 36, "costClp": 11878, "conversions": 0,
                     "dateFrom": "2026-10-08", "dateTo": "2026-10-08"},
        "history": [{"dateFrom": "2026-10-08", "dateTo": "2026-10-08", "impressions": 479,
                     "clicks": 36, "costClp": 11878, "conversions": 0}],
        "campaignHistory": [{"campaignId": "123", "name": "Campaña detenida", "status": "PAUSED",
                              "firstSeen": "2026-10-08", "lastSeen": "2026-10-08"}],
    }), encoding="utf-8")
    monkeypatch.setattr(sync, "OUT", output)
    result = normalize([], "2026-10-09", "2026-10-09")
    assert result["metrics"]["clicks"] == 36
    assert result["history"][-1]["dateFrom"] == "2026-10-08"
    assert result["activityRows"] == 0
    assert result["campaignIds"] == ["123"]


def _term(day, term, clicks, cost, **extra):
    return {"date": day, "term": term, "impressions": clicks * 10, "clicks": clicks, "costClp": cost,
            "conversions": 0.0, "averageCpc": None, "ctr": 0.1, **extra}


def _stored(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_report_history_accumulates_days_and_replaces_partial_day(tmp_path):
    path = tmp_path / "history.json"
    first = {"searchTerms": [_term("2026-10-08", "a", 2, 400), _term("2026-10-09", "a", 1, 100)]}
    sync.update_report_history(first, None, path)
    # Al día siguiente solo se piden los dos últimos días: el 10-08 debe seguir guardado
    # y el 10-09 (que llegó parcial) debe reemplazarse por la versión completa.
    second = {"searchTerms": [_term("2026-10-09", "a", 3, 700), _term("2026-10-10", "b", 4, 800)]}
    summary = sync.update_report_history(second, None, path)
    rows = _stored(path)["reports"]["searchTerms"]
    assert [(r["date"], r["term"], r["clicks"]) for r in rows] == [
        ("2026-10-08", "a", 2), ("2026-10-09", "a", 3), ("2026-10-10", "b", 4)]
    assert summary["days"] == 3 and summary["from"] == "2026-10-08" and summary["to"] == "2026-10-10"
    assert "averageCpc" not in rows[0] and "ctr" not in rows[0]  # solo valores base, sin nulos de relleno


def test_report_history_seeds_from_previous_file_on_first_run(tmp_path):
    path = tmp_path / "history.json"
    previous = {"searchTerms": [_term("2026-10-08", "viejo", 5, 900)], "conversionActions": [{"name": "Calls"}]}
    sync.update_report_history({"searchTerms": [_term("2026-10-09", "nuevo", 1, 100)]}, previous, path)
    reports = _stored(path)["reports"]
    assert [r["term"] for r in reports["searchTerms"]] == ["viejo", "nuevo"]
    assert "conversionActions" not in reports  # los catálogos sin fecha no se acumulan


def test_report_history_keeps_data_when_a_report_errors_or_is_empty(tmp_path):
    path = tmp_path / "history.json"
    sync.update_report_history({"searchTerms": [_term("2026-10-08", "a", 2, 400)]}, None, path)
    sync.update_report_history({"searchTerms": {"error": "HTTP 400", "rows": []}}, None, path)
    sync.update_report_history({"searchTerms": []}, None, path)
    assert [r["term"] for r in _stored(path)["reports"]["searchTerms"]] == ["a"]


def test_report_history_trims_to_keep_days(tmp_path, monkeypatch):
    path = tmp_path / "history.json"
    monkeypatch.setattr(sync, "HISTORY_KEEP_DAYS", 3)
    for day in ("2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05"):
        sync.update_report_history({"searchTerms": [_term(day, "a", 1, 100)]}, None, path)
    assert _stored(path)["days"] == ["2026-10-03", "2026-10-04", "2026-10-05"]


def test_report_history_tolerates_rows_with_null_date(tmp_path):
    path = tmp_path / "history.json"
    rows = [_term("2026-10-09", "a", 1, 100), {**_term(None, "sin fecha", 1, 50)}]
    sync.update_report_history({"searchTerms": rows}, None, path)
    sync.update_report_history({"searchTerms": rows}, None, path)
    stored = _stored(path)
    assert stored["days"] == ["2026-10-09"]
    assert len(stored["reports"]["searchTerms"]) == 2  # la fila sin fecha se reemplaza, no se duplica


def _settings_row(**campaign):
    return {"campaign": {"id": "1", "name": "Campaign #1", "status": "ENABLED",
                         "advertisingChannelType": "SEARCH", "biddingStrategyType": "MAXIMIZE_CLICKS", **campaign},
            "campaignBudget": {"amountMicros": "5000000000"}}


def test_campaign_settings_query_uses_date_time_fields_of_current_api():
    sql = query("2026-10-08", "2026-10-09")  # la de ajustes sale de report_queries
    queries = sync.report_queries("2026-10-08", "2026-10-09")
    assert "campaign.start_date_time" in queries["campaignSettings"]
    assert "campaign.start_date," not in queries["campaignSettings"] and sql


def test_campaign_settings_dates_and_budget_are_normalized():
    rows = sync.compact_report("campaignSettings", [
        _settings_row(startDateTime="2026-10-08 00:00:00", endDateTime="2037-12-30 00:00:00")])
    item = rows[0]
    assert item["startDate"] == "2026-10-08"
    assert item["endDate"] is None  # 2037-12-30 es el «sin fecha de término» de Google
    assert item["dailyBudgetClp"] == 5000


def test_campaign_settings_missing_budget_is_none_not_zero():
    row = _settings_row()
    row.pop("campaignBudget")
    assert sync.compact_report("campaignSettings", [row])[0]["dailyBudgetClp"] is None


def test_campaign_settings_falls_back_to_query_without_dates(monkeypatch):
    calls = []

    def fake_stream(cid, headers, statement):
        calls.append(statement)
        if "start_date_time" in statement:
            raise RuntimeError("HTTP 400: UNRECOGNIZED_FIELD campaign.start_date_time")
        return [_settings_row()]
    monkeypatch.setattr(sync, "search_stream", fake_stream)
    rows = sync.fetch_campaign_settings("123", {}, "SELECT campaign.start_date_time FROM campaign")
    assert rows[0]["biddingStrategy"] == "MAXIMIZE_CLICKS" and rows[0]["dailyBudgetClp"] == 5000
    assert len(calls) == 2 and "start_date_time" not in calls[1]


def test_campaign_settings_other_errors_are_not_swallowed(monkeypatch):
    import pytest

    def boom(cid, headers, statement):
        raise RuntimeError("HTTP 403: PERMISSION_DENIED")
    monkeypatch.setattr(sync, "search_stream", boom)
    with pytest.raises(RuntimeError, match="PERMISSION_DENIED"):
        sync.fetch_campaign_settings("123", {}, "SELECT 1")


def test_geo_regions_get_the_country_name(monkeypatch):
    seen = []

    def fake_stream(cid, headers, statement):
        seen.append(statement)
        return [{"geoTargetConstant": {"resourceName": "geoTargetConstants/2152", "id": "2152", "name": "Chile",
                                       "canonicalName": "Chile", "countryCode": "CL", "targetType": "Country"}}]
    monkeypatch.setattr(sync, "search_stream", fake_stream)
    reports = {"regions": [{"countryCriterionId": "2152", "locationType": "AREA_OF_INTEREST", "clicks": 66},
                           {"countryCriterionId": "2152", "locationType": "LOCATION_OF_PRESENCE", "clicks": 27}]}
    sync.enrich_geo_regions("123", {}, reports)
    assert [r["name"] for r in reports["regions"]] == ["Chile", "Chile"]
    assert reports["regions"][0]["clicks"] == 66 and "'geoTargetConstants/2152'" in seen[0]
    assert len(seen) == 1  # una sola consulta para todas las filas


def test_geo_regions_without_ids_do_not_call_google(monkeypatch):
    def boom(*args):
        raise AssertionError("no debería consultar")
    monkeypatch.setattr(sync, "search_stream", boom)
    sync.enrich_geo_regions("123", {}, {"regions": [{"locationType": "AREA_OF_INTEREST"}]})
    sync.enrich_geo_regions("123", {}, {"regions": {"error": "x"}})


def test_geo_locations_still_get_names_after_refactor(monkeypatch):
    monkeypatch.setattr(sync, "search_stream", lambda *a: [{"geoTargetConstant": {
        "resourceName": "geoTargetConstants/20160", "id": "20160", "name": "Santiago Metropolitan Region",
        "targetType": "Region"}}])
    reports = {"locations": [{"geoTargetConstant": "geoTargetConstants/20160"}]}
    sync.enrich_geo_locations("123", {}, reports)
    assert reports["locations"][0]["name"] == "Santiago Metropolitan Region"


def test_campaign_quality_query_is_campaign_level_and_read_only():
    sql = sync.report_queries("2026-10-08", "2026-10-09")["campaignQuality"]
    assert "FROM campaign" in sql and "metrics.search_budget_lost_impression_share" in sql
    assert "message_chats" not in sql and all(w not in sql.upper() for w in ("MUTATE", "UPDATE", "REMOVE"))
    # sin segmentos incompatibles con las cuotas de impresiones
    assert all(seg not in sql for seg in ("segments.hour", "segments.device", "segments.ad_network_type", "search_term_view"))


def _quality_row(day, cid="1", **vals):
    base = {"campaignId": cid, "date": day, "interactions": None, "invalidClicks": None, "phoneCalls": None,
            "searchImpressionShare": None, "searchBudgetLostImpressionShare": None,
            "searchRankLostImpressionShare": None, "searchTopImpressionShare": None,
            "absoluteTopImpressionPercentage": None, "topImpressionPercentage": None}
    return {**base, **vals}


def test_campaign_quality_fills_metrics_of_the_same_day_only():
    result = {"metrics": {"dateTo": "2026-10-09", "interactions": None, "searchImpressionShare": None,
                          "searchBudgetLostImpressionShare": None},
              "reports": {"campaignQuality": [
                  _quality_row("2026-10-08", interactions="99", searchImpressionShare=0.9),
                  _quality_row("2026-10-09", interactions="52", invalidClicks="1", searchImpressionShare=0.41,
                               searchBudgetLostImpressionShare=0.38)]}}
    sync.apply_campaign_quality(result)
    m = result["metrics"]
    assert m["interactions"] == 52 and m["invalidClicks"] == 1  # no mezcla el 10-08
    assert m["searchImpressionShare"] == 0.41 and m["searchBudgetLostImpressionShare"] == 0.38
    assert "phoneCalls" not in m  # Google no lo devolvió: no se inventa


def test_campaign_quality_does_not_average_shares_across_campaigns():
    result = {"metrics": {"dateTo": "2026-10-09"}, "reports": {"campaignQuality": [
        _quality_row("2026-10-09", cid="1", interactions=10, searchImpressionShare=0.5),
        _quality_row("2026-10-09", cid="2", interactions=5, searchImpressionShare=0.2)]}}
    sync.apply_campaign_quality(result)
    assert result["metrics"]["interactions"] == 15
    assert "searchImpressionShare" not in result["metrics"]  # dos campañas: no se promedia


def test_campaign_quality_ignores_errors_and_missing_day():
    for reports in ({"campaignQuality": {"error": "HTTP 400", "rows": []}}, {"campaignQuality": []},
                    {"campaignQuality": [_quality_row("2026-10-01", interactions=3)]}, {}):
        result = {"metrics": {"dateTo": "2026-10-09", "interactions": None}, "reports": reports}
        sync.apply_campaign_quality(result)
        assert result["metrics"]["interactions"] is None


def test_campaign_quality_report_rows_keep_real_base_numbers_and_campaign():
    rows = sync.compact_report("campaignQuality", [{
        "campaign": {"id": "7", "name": "Campaign #1"}, "segments": {"date": "2026-10-09"},
        "metrics": {"impressions": "800", "clicks": "44", "costMicros": "11267000000", "searchImpressionShare": 0.41}}])
    assert rows[0]["campaignId"] == "7" and rows[0]["clicks"] == 44 and rows[0]["costClp"] == 11267
    assert rows[0]["searchImpressionShare"] == 0.41


def test_report_history_keeps_quality_shares_only_for_campaign_quality(tmp_path):
    path = tmp_path / "history.json"
    quality = {"date": "2026-10-09", "campaignId": "1", "clicks": 41, "impressions": 649, "costClp": 10708,
               "conversions": 0.0, "searchBudgetLostImpressionShare": 0.62, "searchImpressionShare": 0.3,
               "interactions": 44, "averageCpc": 261.0}
    term = {"date": "2026-10-09", "term": "a", "clicks": 1, "impressions": 5, "costClp": 100, "conversions": 0.0,
            "searchBudgetLostImpressionShare": 0.62}
    sync.update_report_history({"campaignQuality": [quality], "searchTerms": [term]}, None, path)
    stored = _stored(path)["reports"]
    kept = stored["campaignQuality"][0]
    assert kept["searchBudgetLostImpressionShare"] == 0.62 and kept["searchImpressionShare"] == 0.3
    assert kept["interactions"] == 44 and "averageCpc" not in kept
    assert "searchBudgetLostImpressionShare" not in stored["searchTerms"][0]  # en los demás informes se siguen descartando


def test_tracking_queries_are_read_only_and_separate_from_conversion_actions():
    queries = sync.report_queries("2026-10-08", "2026-10-09")
    for name in ("accountTracking", "callActionSettings", "callDetails"):
        sql = queries[name].upper()
        assert all(word not in sql for word in ("MUTATE", "UPDATE ", "REMOVE", "MESSAGE_CHATS")), name
    assert "FROM customer" in queries["accountTracking"] and "FROM call_view" in queries["callDetails"]
    assert "segments." not in queries["callDetails"]  # call_view no admite segmentos de fecha
    assert "phone_call_duration_seconds" not in queries["conversionActions"]  # el informe que ya funciona no se toca


def test_account_tracking_and_call_action_settings_are_normalized_without_inventing_values():
    track = sync.compact_report("accountTracking", [{"customer": {
        "autoTaggingEnabled": True, "conversionTrackingSetting": {"conversionTrackingStatus": "CONVERSION_TRACKING_MANAGED_BY_SELF"}}}])[0]
    assert track["autoTaggingEnabled"] is True and track["conversionTrackingStatus"].startswith("CONVERSION_TRACKING")
    missing = sync.compact_report("accountTracking", [{"customer": {}}])[0]
    assert missing["autoTaggingEnabled"] is None  # sin dato: no se convierte en False
    action = sync.compact_report("callActionSettings", [{"conversionAction": {
        "id": "7", "name": "Calls from ads", "type": "AD_CALL", "phoneCallDurationSeconds": 60, "primaryForGoal": True}}])[0]
    assert action["phoneCallDurationSeconds"] == 60 and action["primaryForGoal"] is True
    no_duration = sync.compact_report("callActionSettings", [{"conversionAction": {"id": "8", "name": "x"}}])[0]
    assert no_duration["phoneCallDurationSeconds"] is None


def test_call_details_keep_duration_status_and_date_for_history():
    row = {"campaign": {"id": "5", "name": "Campaign #1"},
           "callView": {"callDurationSeconds": "34", "callStatus": "RECEIVED", "type": "MOBILE_CALL_FROM_ADS",
                        "startCallDateTime": "2026-10-09 10:02:11", "callerAreaCode": "9", "callerCountryCode": "CL"}}
    call = sync.compact_report("callDetails", [row, {"callView": {}}])
    assert call[0]["durationSeconds"] == 34 and call[0]["status"] == "RECEIVED" and call[0]["date"] == "2026-10-09"
    assert call[1]["durationSeconds"] is None  # llamada sin duración informada: no se inventa 0
    assert "phoneNumber" not in call[0] and "callerNumber" not in call[0]  # no se guarda el número de nadie


def test_sincronizador_es_solo_lectura():
    """Regla del dueño: las campañas solo se leen. Nada de llamadas mutate a Google Ads."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "tools" / "panel" / "sync_google_ads.py").read_text(encoding="utf-8")
    assert "mutate" not in src.lower()
    assert "googleAds:searchStream" in src
