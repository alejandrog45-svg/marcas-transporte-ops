import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sync_suggestions_firestore", Path(__file__).parents[1] / "tools" / "panel" / "sync_suggestions_firestore.py")
sg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sg)


def _t(day, term, clicks, cost):
    return {"date": day, "term": term, "clicks": clicks, "impressions": clicks * 10, "costClp": cost,
            "conversions": 0.0, "campaignName": "Campaign #1"}


def _data(terms):
    return {"lastSync": "2026-10-09T11:45:00Z", "customerId": "2035504421",
            "campaigns": [{"name": "Campaign #1", "status": "ENABLED", "clicks": 41}],
            "history": [{"dateFrom": "2026-10-08", "clicks": 52, "impressions": 794},
                        {"dateFrom": "2026-10-09", "clicks": 41, "impressions": 649}],
            "reports": {"searchTerms": terms}}


def test_merge_terms_sums_days_and_ignores_case():
    merged = sg.merge_terms([_t("2026-10-08", "Transfer Aeropuerto", 2, 500), _t("2026-10-09", "transfer aeropuerto", 3, 904),
                             _t("2026-10-09", "otro", 1, 50), {"date": "x", "clicks": 9}])
    top = max(merged, key=lambda r: r["clicks"])
    assert (top["term"], top["clicks"], top["costClp"]) == ("Transfer Aeropuerto", 5, 1404)
    assert len(merged) == 2  # la fila sin término se descarta


def test_best_term_uses_accumulated_history_not_a_single_day():
    fresh = [_t("2026-10-09", "dia unico", 4, 100)]  # una fila diaria con más clics que cada fila del historial
    history = {"reports": {"searchTerms": [_t("2026-10-08", "acumulado", 3, 300), _t("2026-10-09", "acumulado", 3, 300),
                                           _t("2026-10-09", "dia unico", 4, 100)]}}
    out = sg.build_suggestions(_data(fresh), history)
    best = next(s for s in out["suggestions"] if s["title"] == "Agregar palabras de alto rendimiento")
    assert "«acumulado»: 6 clics" in best["data"]["evidence"]


def test_without_history_falls_back_to_fresh_rows():
    out = sg.build_suggestions(_data([_t("2026-10-09", "solo fresco", 2, 80)]), {})
    best = next(s for s in out["suggestions"] if s["title"] == "Agregar palabras de alto rendimiento")
    assert "«solo fresco»: 2 clics" in best["data"]["evidence"]


def _titles(out):
    return {s["title"]: s for s in out["suggestions"]}


def test_budget_rule_flags_high_lost_share_with_real_numbers():
    data = _data([_t("2026-10-09", "a", 3, 100)])
    data["metrics"] = {"searchBudgetLostImpressionShare": 0.6228, "searchImpressionShare": 0.2957,
                       "searchRankLostImpressionShare": 0.0815}
    s = _titles(sg.build_suggestions(data, {}))["Evaluar si el presupuesto limita el alcance"]
    assert s["kind"] == "REVISAR" and "62.3 %" in s["data"]["evidence"] and "29.6 %" in s["data"]["evidence"]
    assert "no se cambia nada solo" in s["action"]


def test_budget_rule_is_quiet_when_loss_is_low_and_honest_when_missing():
    low = _data([_t("2026-10-09", "a", 3, 100)])
    low["metrics"] = {"searchBudgetLostImpressionShare": 0.03}
    assert _titles(sg.build_suggestions(low, {}))["Evaluar si el presupuesto limita el alcance"]["kind"] == "SIN ALERTA"
    none = _data([_t("2026-10-09", "a", 3, 100)])
    none["metrics"] = {"searchBudgetLostImpressionShare": None}
    s = _titles(sg.build_suggestions(none, {}))["Evaluar si el presupuesto limita el alcance"]
    assert s["kind"] == "DATOS INSUFICIENTES" and "No se inventa" in s["data"]["reason"]
