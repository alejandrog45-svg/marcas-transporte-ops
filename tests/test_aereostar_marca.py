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


def test_cada_panel_usa_solo_los_colores_de_su_marca():
    b = _build()
    assert "2563eb" not in b.ut_recolor("a{color:#2563eb}b{fill:rgb(37 99 235/var(--x))}").lower()
    assert "#ed1c24" in b.ut_recolor("a{color:#2563eb}")        # UberTransfer: rojo del logo
    assert "#e96712" in b.ae_recolor("a{color:#2563eb}")        # Aereostar: naranja del logo


def test_movimiento_es_css_puro_y_respeta_reducir_movimiento():
    css = (ROOT / "tools" / "panel" / "extra.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    # fill-mode «backwards»: al terminar la animación la sección vuelve a su estilo normal (sin transform residual)
    assert "section{animation:secIn .45s var(--ease) backwards}" in css
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    assert "countUp" not in tpl and "requestAnimationFrame" not in tpl   # sin contadores animados: no alteran las cifras que comprueban las verificaciones

