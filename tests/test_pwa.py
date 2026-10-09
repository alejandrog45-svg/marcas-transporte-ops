import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[1]
SITE = ROOT / "site"


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
        assert Image.open(path).size == (w, h)
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


def test_template_marks_pwa_block_and_build_strips_it_for_aereostar():
    tpl = (ROOT / "tools" / "panel" / "template.html").read_text(encoding="utf-8")
    assert tpl.count("<!--PWA-->") == 1 and tpl.count("<!--/PWA-->") == 1
    assert tpl.count("<!--AEICON") == 1 and tpl.count("AEICON-->") == 1
    # el script de cabecera no puede ser un <script> simple: build.py usa ese texto para separar la app
    head_script = tpl[tpl.index("<!--PWA-->"):tpl.index("<!--/PWA-->")]
    assert "<script>" not in head_script
    build = (ROOT / "tools" / "panel" / "build.py").read_text(encoding="utf-8")
    assert "<!--PWA-->" in build and "AEICON" in build
