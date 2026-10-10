"""Cada marca con sus propias recomendaciones: nada de UberTransfer puede aparecer en el panel de Aereostar."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "tools" / "panel"


def _cargar(nombre, archivo, monkeypatch, marca=None):
    if marca is None:
        monkeypatch.delenv("GOOGLE_ADS_BRAND", raising=False)
    else:
        monkeypatch.setenv("GOOGLE_ADS_BRAND", marca)
    spec = importlib.util.spec_from_file_location(nombre, PANEL / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sugerencias_firestore_por_marca(monkeypatch):
    ut = _cargar("sf_ut", "sync_suggestions_firestore.py", monkeypatch)
    assert ut.DOCUMENT == "panel/aiSuggestions" and ut.ADS_FILE.name == "google_ads_ubertransfer.json"
    ae = _cargar("sf_ae", "sync_suggestions_firestore.py", monkeypatch, "Aereostar")
    assert ae.DOCUMENT == "panel/aiSuggestions_aereostar"
    assert ae.ADS_FILE.name == "google_ads_aereostar.json" and ae.HISTORY_FILE.name == "google_ads_history_aereostar.json"


def test_sugerencias_ia_por_marca(monkeypatch):
    ut = _cargar("ia_ut", "ai_enrich_suggestions.py", monkeypatch)
    assert ut.OUT_FILE.name == "ai_suggestions_latest.json"
    assert "UberTransfer" in ut.build_prompt({"cobertura": {}}, "Campaign")
    ae = _cargar("ia_ae", "ai_enrich_suggestions.py", monkeypatch, "Aereostar")
    assert ae.OUT_FILE.name == "ai_suggestions_aereostar_latest.json"
    prompt = ae.build_prompt({"cobertura": {}}, "Campaign #1")
    assert "Aereostar" in prompt and "UberTransfer" not in prompt


def test_panel_aereostar_no_lee_el_documento_de_ubertransfer():
    tpl = (PANEL / "template.html").read_text(encoding="utf-8")
    assert tpl.count('const SUGDOC="aiSuggestions"') == 1 and 'doc("aiSuggestions")' not in tpl
    spec = importlib.util.spec_from_file_location("panel_build_sug", PANEL / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    page = mod.brand_aereostar(tpl)
    assert 'const SUGDOC="aiSuggestions_aereostar"' in page and 'const SUGDOC="aiSuggestions"' not in page


def test_reglas_de_firestore_cubren_el_documento_de_cada_marca():
    reglas = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    for doc in ("/panel/aiSuggestions {", "/panel/aiSuggestions_aereostar {"):
        i = reglas.index(doc)
        assert "allow read: if autorizado();" in reglas[i:i + 120] and "allow write: if false;" in reglas[i:i + 120]
