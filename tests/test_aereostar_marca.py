"""El panel de Aereostar usa su logo y los colores del logo (no los de UberTransfer)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _build():
    spec = importlib.util.spec_from_file_location("panel_build", ROOT / "tools" / "panel" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_iconos_de_aereostar_existen():
    for n in ("logo-128.png", "favicon-32.png", "apple-touch-icon.png", "aereostar-192.png", "aereostar-512.png"):
        assert (ROOT / "site" / "aereostar" / "icons" / n).stat().st_size > 500, n


def test_recolor_pasa_azules_a_naranja():
    b = _build()
    out = b.ae_recolor("a{color:#2563eb}b{background:rgb(37 99 235/var(--x))}c{color:#1d4ed8}")
    assert "2563eb" not in out and "37 99 235" not in out and "1d4ed8" not in out
    assert "#e96712" in out


def test_panel_aereostar_lleva_logo_y_menu_completo():
    b = _build()
    page = b.brand_aereostar((ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8"))
    assert "/aereostar/icons/logo-128.png" in page
    assert "#ed1c24" not in page and "#e96712" in page
    assert "META.fullMenu" in page
