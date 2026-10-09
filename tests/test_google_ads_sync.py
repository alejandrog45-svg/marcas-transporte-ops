import json
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "panel" / "sync_google_ads.py"
SPEC = importlib.util.spec_from_file_location("sync_google_ads", MODULE_PATH)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
normalize, query = sync.normalize, sync.query


def test_query_is_report_only():
    sql = query("2026-10-08", "2026-10-08")
    assert "metrics.clicks" in sql
    assert all(word not in sql.upper() for word in ("MUTATE", "UPDATE", "REMOVE"))


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
