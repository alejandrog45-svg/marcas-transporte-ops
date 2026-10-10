"""Aislamiento por marca: cada marca usa sus propios archivos, documento de Firestore y cuenta de Ads."""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "tools" / "panel"))


def _reload(name, brand, monkeypatch):
    if brand is None:
        monkeypatch.delenv("ADS_BRAND", raising=False)
    else:
        monkeypatch.setenv("ADS_BRAND", brand)
    sys.modules.pop(name, None)
    return importlib.import_module(name)


def test_suggestions_modules_default_to_ubertransfer_unchanged(monkeypatch):
    fs = _reload("sync_suggestions_firestore", None, monkeypatch)
    ai = _reload("ai_enrich_suggestions", None, monkeypatch)
    assert fs.DOCUMENT == "panel/aiSuggestions" and fs.ADS_FILE.name == "google_ads_ubertransfer.json"
    assert ai.OUT_FILE.name == "ai_suggestions_latest.json" and ai.HISTORY_FILE.name == "google_ads_history_ubertransfer.json"
    assert "UberTransfer" in ai.build_prompt({"x": {}}, "C")


def test_suggestions_modules_for_aereostar_never_touch_ubertransfer_files(monkeypatch):
    fs = _reload("sync_suggestions_firestore", "aereostar", monkeypatch)
    ai = _reload("ai_enrich_suggestions", "aereostar", monkeypatch)
    assert fs.DOCUMENT == "panel/aiSuggestions_aereostar"
    assert "ubertransfer" not in fs.ADS_FILE.name and "ubertransfer" not in fs.HISTORY_FILE.name
    assert ai.OUT_FILE.name == "ai_suggestions_aereostar.json"
    assert "ubertransfer" not in ai.ADS_FILE.name and "UberTransfer" not in ai.build_prompt({"x": {}}, "C")
    _reload("sync_suggestions_firestore", None, monkeypatch)
    _reload("ai_enrich_suggestions", None, monkeypatch)


def test_firestore_rules_allow_reading_aereostar_suggestions_read_only():
    rules = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    block = rules.split("match /panel/aiSuggestions_aereostar {")[1].split("}")[0]
    assert "allow read: if autorizado();" in block and "allow write: if false;" in block
