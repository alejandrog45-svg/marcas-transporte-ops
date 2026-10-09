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
