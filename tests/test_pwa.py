import json
import struct
from pathlib import Path

ROOT = Path(__file__).parents[1]
SITE = ROOT / "site"


def _png_size(path):
    """Ancho y alto leídos de la cabecera IHDR del PNG (sin librerías de imagen)."""
    data = path.read_bytes()[:24]
    assert data[1:4] == b"PNG", path
    return struct.unpack(">II", data[16:24])


def _manifest():
    return json.loads((SITE / "manifest.webmanifest").read_text(encoding="utf-8"))


def test_manifest_is_installable_and_icons_exist_with_declared_size():
    m = _manifest()
    assert m["display"] == "standalone" and m["start_url"] == "/" and m["scope"] == "/"
    assert m["name"] and m["short_name"] and m["theme_color"].startswith("#")
    purposes = {i["purpose"] for i in m["icons"]}
    assert {"any", "maskable"} <= purposes  # Chrome pide un ícono normal y uno maskable
    for icon in m["icons"]:
        path = SITE / icon["src"].lstrip("/")
        assert path.exists(), icon["src"]
        w, h = (int(x) for x in icon["sizes"].split("x"))
        assert _png_size(path) == (w, h)
    assert {"192x192", "512x512"} <= {i["sizes"] for i in m["icons"]}


def test_service_worker_never_caches_version_login_or_other_origins():
    sw = (SITE / "sw.js").read_text(encoding="utf-8")
    assert "/__/" in sw and "version.json" in sw  # el inicio de sesión y la comprobación de versión no se guardan
    assert "url.origin !== self.location.origin" in sw
    assert "req.method !== 'GET'" in sw
    assert "skipWaiting" in sw and "clients.claim" in sw


def test_csp_allows_manifest_and_worker_but_stays_restrictive():
    cfg = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))
    csp = next(h["value"] for h in cfg["hosting"]["headers"][0]["headers"] if h["key"] == "Content-Security-Policy")
    assert "manifest-src 'self'" in csp and "worker-src 'self'" in csp
    assert "default-src 'none'" in csp and "frame-ancestors 'none'" in csp


def test_template_marks_pwa_block_and_build_adapts_it_for_aereostar():
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    assert tpl.count("<!--PWA-->") == 1 and tpl.count("<!--/PWA-->") == 1
    assert tpl.count("<!--AEICON") == 1 and tpl.count("AEICON-->") == 1
    # el script de cabecera no puede ser un <script> simple: build.py usa ese texto para separar la app
    head_script = tpl[tpl.index("<!--PWA-->"):tpl.index("<!--/PWA-->")]
    assert "<script>" not in head_script
    build = (ROOT / "tools" / "panel" / "build.py").read_text(encoding="utf-8")
    assert "<!--PWA-->" in build and "AEICON" in build


def test_pwa_app_code_runs_after_login_not_in_the_pre_login_gate():
    # build.py corta la plantilla en "Acceso privado y nube": lo de antes es la app (se ejecuta
    # tras descifrar y ya tiene META); lo de después corre al cargar, sin META. Si el código de la
    # PWA queda después de esa marca, el script de acceso falla y el login se cuelga.
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    mark = tpl.index("/* ===== Acceso privado y nube")
    assert tpl.index("App instalable (PWA), badge") < mark
    assert tpl.index("const PANEL_VERSION=") < mark
    assert tpl.index("function vbCheck") < mark


def test_aereostar_tiene_su_propia_pwa():
    """Aereostar es instalable con su manifiesto, su service worker y sus íconos, sin pisar los de UberTransfer."""
    base = SITE / "aereostar"
    m = json.loads((base / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert m["display"] == "standalone" and m["scope"] == "/aereostar/" and m["start_url"] == "/aereostar/"
    assert m["id"] == "/aereostar/" and m["short_name"] == "Aereostar" and m["theme_color"] == "#0b0b0b"
    assert {"any", "maskable"} <= {i["purpose"] for i in m["icons"]}
    for icon in m["icons"]:
        assert icon["src"].startswith("/aereostar/icons/")
        path = SITE / icon["src"].lstrip("/")
        w, h = (int(x) for x in icon["sizes"].split("x"))
        assert _png_size(path) == (w, h), icon["src"]
    sw = (base / "sw.js").read_text(encoding="utf-8")
    assert "ae-html-" in sw and "ae-static-" in sw and "ut-" not in sw          # cachés propios
    assert "/aereostar/icons/" in sw and "'/icons/'" not in sw                  # solo sus propios íconos
    assert "/__/" in sw and "version.json" in sw and "url.origin !== self.location.origin" in sw
    assert "skipWaiting" in sw and "clients.claim" in sw


def test_pagina_aereostar_registra_su_pwa_con_alcance_propio():
    import importlib.util
    spec = importlib.util.spec_from_file_location("panel_build", ROOT / "tools" / "panel" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    page = mod.brand_aereostar((ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8"))
    assert 'href="/aereostar/manifest.webmanifest"' in page and 'href="/manifest.webmanifest"' not in page
    assert 'register("/aereostar/sw.js",{scope:"/aereostar/"})' in page and 'register("/sw.js")' not in page
    assert 'content="#0b0b0b"' in page and 'content="#ed1c24"' not in page
    assert '"/icons/' not in page and "'/icons/" not in page and "/aereostar/aereostar/" not in page
    assert 'apple-mobile-web-app-title" content="Aereostar"' in page
    assert "PWA_ON=(META.plannerActive===false||!!META.fullMenu)" in page

