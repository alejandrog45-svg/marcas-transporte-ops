import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "panel" / "ai_enrich_suggestions.py"
SPEC = importlib.util.spec_from_file_location("ai_enrich_suggestions", MODULE_PATH)
ai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ai)


def _row(day, term, clicks, cost, **extra):
    return {"date": day, "term": term, "impressions": clicks * 10, "clicks": clicks, "costClp": cost,
            "conversions": 0.0, **extra}


def _data():
    return {
        "lastSync": "2026-10-09T11:45:00Z", "customerId": "2035504421", "campaignNames": ["Campaign #1"],
        "metrics": {"conversions": 0.0},
        "history": [
            {"dateFrom": "2026-10-08", "impressions": 794, "clicks": 52, "costClp": 15068, "conversions": 0.0},
            {"dateFrom": "2026-10-09", "impressions": 649, "clicks": 41, "costClp": 10708, "conversions": 0.0},
        ],
        "reports": {
            "searchTerms": [_row("2026-10-08", "Transfer aeropuerto", 2, 500), _row("2026-10-09", "transfer aeropuerto", 3, 904)],
            "hourly": [{"date": "2026-10-08", "hour": 8, "clicks": 7, "impressions": 90, "costClp": 3063, "conversions": 0.0}],
            "devices": [{"date": "2026-10-08", "device": "MOBILE", "clicks": 40, "impressions": 700, "costClp": 9000, "conversions": 0.0}],
        },
    }


def test_facts_sum_all_days_and_flag_partial_day():
    facts = ai.build_facts(_data(), {})
    top = facts["terminos_mas_clics"]["filas"][0]
    assert (top["termino"], top["clics"], top["costoClp"]) == ("transfer aeropuerto", 5, 1404)
    assert [d["diaParcial"] for d in facts["dias"]["filas"]] == [False, True]
    assert facts["dias"]["filas"][0]["ctrPct"] == 6.55 and facts["dias"]["filas"][0]["cpcClp"] == 290
    assert facts["cobertura"]["diasConDetalle"] == 2


def test_facts_prefer_accumulated_history_over_fresh_rows():
    history = {"reports": {"searchTerms": [_row("2026-10-01", "viejo", 9, 100), _row("2026-10-09", "nuevo", 1, 10)]}}
    facts = ai.build_facts(_data(), history)
    assert [r["termino"] for r in facts["terminos_mas_clics"]["filas"]] == ["viejo", "nuevo"]


def test_validate_accepts_numbers_from_cited_facts_in_any_format():
    facts = ai.build_facts(_data(), {})
    good = [{"title": "Revisar «transfer aeropuerto»", "action": "Comparar con $1.404 de costo.",
             "reason": "Sumó 5 clics y CTR de 6,55 %.", "refs": ["terminos_mas_clics", "dias"], "confidence": "Media"}]
    valid, rejected = ai.validate(good, facts)
    assert len(valid) == 1 and not rejected


def test_validate_rejects_invented_numbers_and_missing_refs():
    facts = ai.build_facts(_data(), {})
    invented = {"title": "Subir tráfico", "action": "Pasar de 5 a 300 clics.", "reason": "x",
                "refs": ["terminos_mas_clics"], "confidence": "Media"}
    no_refs = {"title": "Algo sin evidencia", "action": "Hacer algo.", "reason": "x", "refs": [], "confidence": "Media"}
    bad_ref = {"title": "Cita inventada", "action": "x", "reason": "x", "refs": ["no_existe"], "confidence": "Media"}
    valid, rejected = ai.validate([invented, no_refs, bad_ref], facts)
    assert valid == [] and len(rejected) == 3
    assert "300" in rejected[0]


def test_validate_caps_count_and_normalizes_confidence():
    facts = ai.build_facts(_data(), {})
    many = [{"title": f"Idea {chr(65 + i)}", "action": "Revisar.", "reason": "x", "refs": ["dias"], "confidence": "Alta"} for i in range(9)]
    valid, _ = ai.validate(many, facts)
    assert len(valid) == ai.MAX_SUGGESTIONS and {v["confidence"] for v in valid} == {"Baja"}


def test_enrich_attaches_evidence_from_facts_not_from_model(monkeypatch):
    monkeypatch.setattr(ai, "call_gemini", lambda *a, **k: ([
        {"title": "Revisar término", "action": "Comparar.", "reason": "5 clics.", "refs": ["terminos_mas_clics"], "confidence": "Media"}], "modelo-x"))
    result = ai.enrich(_data(), {}, "clave", "modelo-x")
    assert result["suggestions"][0]["evidence"]["terminos_mas_clics"]["filas"][0]["clics"] == 5
    assert "modelo-x" in result["source"] and result["detailDays"] == 2


def _wire(monkeypatch, tmp_path, data=True):
    ads = tmp_path / "ads.json"
    if data:
        ads.write_text(json.dumps(_data()), encoding="utf-8")
    out = tmp_path / "out.json"
    monkeypatch.setattr(ai, "ADS_FILE", ads)
    monkeypatch.setattr(ai, "HISTORY_FILE", tmp_path / "no_hay_historial.json")
    monkeypatch.setattr("sys.argv", ["ai", "--out", str(out)])
    return out


def test_main_without_key_does_nothing_and_does_not_fail(monkeypatch, tmp_path):
    out = _wire(monkeypatch, tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert ai.main() == 0 and not out.exists()


def test_main_survives_gemini_failure(monkeypatch, tmp_path, capsys):
    out = _wire(monkeypatch, tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "clave-de-prueba")

    def boom(*args, **kwargs):
        raise RuntimeError("Gemini HTTP 503")
    monkeypatch.setattr(ai, "call_gemini", boom)
    assert ai.main() == 0 and not out.exists()
    assert "clave-de-prueba" not in capsys.readouterr().out


def test_main_writes_validated_output(monkeypatch, tmp_path):
    out = _wire(monkeypatch, tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(ai, "call_gemini", lambda *a, **k: ([
        {"title": "Revisar", "action": "Comparar.", "reason": "Hay 2 días de historial.", "refs": ["cobertura"], "confidence": "Baja"},
        {"title": "Inventada", "action": "Llegar a 999 clics.", "reason": "x", "refs": ["dias"], "confidence": "Media"}], "modelo-x"))
    assert ai.main() == 0
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert [s["title"] for s in saved["suggestions"]] == ["Revisar"] and len(saved["rejected"]) == 1


class _Resp:
    def __init__(self, status, text=None):
        self.status_code = status
        self._text = text

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self._text}]}}]}


def test_call_gemini_falls_back_to_next_model_when_first_is_saturated(monkeypatch):
    import requests
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url.split("/models/")[1].split(":")[0])
        return _Resp(503) if "primero" in url else _Resp(200, '[{"title": "ok"}]')
    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(ai.time, "sleep", lambda s: None)
    monkeypatch.setattr(ai, "FALLBACK_MODELS", ("segundo",))
    parsed, used = ai.call_gemini("p", "clave", "primero")
    assert used == "segundo" and parsed == [{"title": "ok"}]
    assert calls == ["primero", "primero", "segundo"]  # un reintento corto antes de cambiar de modelo


def test_call_gemini_raises_when_every_model_fails(monkeypatch):
    import pytest
    import requests
    monkeypatch.setattr(requests, "post", lambda url, **kw: _Resp(503))
    monkeypatch.setattr(ai.time, "sleep", lambda s: None)
    monkeypatch.setattr(ai, "FALLBACK_MODELS", ("b",))
    with pytest.raises(RuntimeError, match="Gemini no respondió"):
        ai.call_gemini("p", "clave", "a")


def _build_module():
    spec = importlib.util.spec_from_file_location("panel_build", Path(__file__).parents[1] / "tools" / "panel" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_reads_ai_suggestions_and_ignores_missing_or_corrupt_file(tmp_path):
    build = _build_module()
    assert build.read_ai_suggestions(tmp_path / "no_existe.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{no es json", encoding="utf-8")
    assert build.read_ai_suggestions(bad) is None
    good = tmp_path / "ai.json"
    good.write_text(json.dumps({
        "source": "IA (m)", "generatedAt": "2026-10-09T19:00:00Z", "adsLastSync": "x", "detailDays": 3,
        "rejected": ["una"], "extra": "no debe pasar",
        "suggestions": [
            {"title": "Revisar", "action": "a", "reason": "r", "confidence": "Alta", "refs": ["dias"], "evidence": {"dias": {"filas": []}}},
            {"title": "   ", "action": "sin título se descarta"},
        ]}), encoding="utf-8")
    out = build.read_ai_suggestions(good)
    assert out["rejected"] == 1 and out["detailDays"] == 3 and "extra" not in out
    assert [s["title"] for s in out["suggestions"]] == ["Revisar"]
    assert out["suggestions"][0]["confidence"] == "Baja"  # una confianza no permitida se baja a "Baja"
