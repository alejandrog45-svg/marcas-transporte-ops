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



def test_fondo_fotografico_solo_en_ubertransfer_y_liviano():
    b = _build()
    foto = ROOT / "site" / "bg" / "ubertransfer-fondo.jpg"
    assert foto.exists() and foto.stat().st_size < 150_000          # liviano: no frena la carga del panel
    css = (ROOT / "tools" / "panel" / "extra.css").read_text(encoding="utf-8")
    assert "pointer-events:none" in css and "z-index:-1" in css       # no tapa ni recibe clics: queda detrás de todo
    assert "var(--bg-img,none)" in css                                # sin variable no hay foto (Aereostar)
    assert "ubertransfer-fondo.jpg" in b.UT_BG
    assert "ubertransfer-fondo" not in b.ae_recolor(css)               # Aereostar no hereda la foto de UberTransfer


def test_fondo_de_aereostar_propio_liviano_y_sin_logos_de_ubertransfer():
    b = _build()
    foto = ROOT / "site" / "bg" / "aereostar-fondo.jpg"
    assert foto.exists() and foto.stat().st_size < 100_000
    assert "aereostar-fondo.jpg" in b.AE_BG and "ubertransfer" not in b.AE_BG
    assert "aereostar-fondo.jpg" not in b.UT_BG                        # cada marca con su propia foto
    page = b.brand_aereostar((ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8"))
    assert "ubertransfer-fondo" not in page and "logouber" not in page and "/icons/ubertransfer" not in page


def test_cada_marca_conserva_su_logo_original():
    """Regla antirretroceso: el logo de UberTransfer y el de Aereostar no se mezclan ni se reemplazan."""
    import subprocess
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    assert tpl.count("/icons/logo-128.png") >= 2                      # UberTransfer usa su logo de siempre
    page = _build().brand_aereostar(tpl)
    assert "/aereostar/icons/logo-128.png" in page and 'src="/icons/' not in page   # Aereostar usa solo el suyo
    # Los archivos de logo que ya estaban en main no se modifican ni se borran (solo se permite agregar nuevos).
    out = subprocess.run(["git", "diff", "--name-status", "origin/main", "--",
                          "site/icons", "site/aereostar/icons", "docs/archivo/logo"],
                         cwd=ROOT, capture_output=True, text=True)
    if out.returncode == 0:                                          # sin origin/main (otro entorno) no se puede comparar
        cambios = [l for l in out.stdout.splitlines() if l and l[0] in "MDR"]
        assert not cambios, cambios


def test_barra_de_marca_en_celular_con_el_logo_de_cada_marca():
    """En celular no existe el menú lateral: la barra #mbrand muestra el logo y el nombre de CADA marca."""
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    assert tpl.count('id="mbrand"') == 1 and 'src="/icons/logo-128.png" alt="Logo UberTransfer"' in tpl
    page = _build().brand_aereostar(tpl)
    assert 'class="mb-logo" src="/aereostar/icons/logo-128.png" alt="Logo Aereostar"' in page
    assert "UberTransfer" not in page[page.index('id="mbrand"'):page.index('id="mbrand"') + 400]
    css = (ROOT / "tools" / "panel" / "extra.css").read_text(encoding="utf-8")
    assert "#mbrand{display:flex" in css and "min-width:1024px" in css  # banner también en escritorio
