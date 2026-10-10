#!/usr/bin/env python3
"""Arma los paneles de UberTransfer y de Aereostar con datos reales del repo.

Entradas (todas en el repo):
  data/keyword_planner_AAAAMMDD.csv (+ .meta.json)  frases exportadas del Planificador de Google Ads
  data/forecast_google.json                        previsión oficial de Google (sin gasto)
  data/audit_latest.json                           auditoría técnica de ubertransfer.cl (diaria)
  data/audit_aereostar_latest.json                 auditoría técnica de aereostar.cl (manual; opcional)
  data/keyword_planner_rubros_*.json               ampliación a otros rubros (solo panel de UberTransfer)
  data/panel_data*.enc.json                        texto cifrado de los datos (se reutiliza si las entradas no cambiaron)
  tools/panel/template.html, ias.html, ias_aereostar.html, extra.css, tw.config.js

Salidas (dos paneles: UberTransfer y Aereostar, misma plantilla):
  site/index.html, site/aereostar/index.html   lo que se publica en Firebase Hosting (datos CIFRADOS con AES-256-GCM)
  site/version.json, site/aereostar/version.json   para que cada panel compruebe que se ve la versión publicada
  docs/panel_keywords.html, docs/panel_aereostar.html   copias LOCALES en claro (ignoradas por Git)
  data/panel_data.enc.json, data/panel_data_aereostar.enc.json   texto cifrado (se sube a Git)

Uso:  python tools/panel/build.py
Requiere Node.js (solo para compilar el CSS de Tailwind, una vez por armado).
No hace ninguna llamada de red salvo `npm install` la primera vez.
"""
import re
import csv, datetime, hashlib, io, json, os, shutil, subprocess, sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
ROOT = TOOL.parents[1]
DATA = ROOT / "data"
BUILD = TOOL / ".build"


def read_text(p):
    return Path(p).read_text(encoding="utf-8")


def read_google_ads_status(path, brand, default_campaign_ids=()):
    """Carga solo la configuración no secreta del conector Google Ads de una marca.

    La conexión real queda fuera del armado: aquí solo se valida la identidad de la
    cuenta/campaña y se deja explícito que el modo permitido es de lectura.
    """
    p = Path(path)
    if not p.exists():
        return {"brand": brand, "customerId": None, "campaignIds": list(default_campaign_ids),
                "mode": "read_only", "status": "pending_api", "lastSync": None,
                "source": "Google Ads API", "metrics": None}
    obj = json.loads(read_text(p))
    if obj.get("brand") != brand:
        raise SystemExit(f"Google Ads: la marca de {p.name} no coincide con {brand}.")
    customer = str(obj.get("customerId") or "")
    if customer and (not customer.isdigit() or len(customer) != 10):
        raise SystemExit(f"Google Ads: customerId inválido en {p.name}.")
    if obj.get("mode") != "read_only":
        raise SystemExit(f"Google Ads: el conector de {brand} debe ser read_only.")
    ids = obj.get("campaignIds", [])
    if not isinstance(ids, list) or any(not str(x).isdigit() for x in ids):
        raise SystemExit(f"Google Ads: campaignIds inválidos en {p.name}.")
    if any(k.lower() in {"token", "clientsecret", "client_secret", "refresh_token", "private_key"}
           for k in obj):
        raise SystemExit(f"Google Ads: no se permiten credenciales en {p.name}.")
    names = obj.get("campaignNames", [])
    if not isinstance(names, list) or any(not isinstance(x, str) or not x.strip() for x in names):
        raise SystemExit(f"Google Ads: campaignNames inválidos en {p.name}.")
    reports = obj.get("reports", {})
    if not isinstance(reports, dict):
        raise SystemExit(f"Google Ads: reports inválidos en {p.name}.")
    return {"brand": brand, "customerId": customer or None, "campaignIds": [str(x) for x in ids],
            "campaignNames": names, "campaignHistory": obj.get("campaignHistory", []),
            "adHistory": obj.get("adHistory", []), "alerts": obj.get("alerts", []),
            "mode": "read_only", "status": obj.get("status", "pending_api"),
            "lastSync": obj.get("lastSync"), "source": "Google Ads API", "metrics": obj.get("metrics"),
            "history": obj.get("history", []), "campaigns": obj.get("campaigns", []),
            "reports": reports, "observed": obj.get("observed")}


def read_ai_suggestions(path):
    """Sugerencias redactadas por la IA (Gemini). Es un extra: si falta o viene dañado, el panel se arma sin él."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        obj = json.loads(read_text(p))
    except ValueError:
        return None
    items = obj.get("suggestions") if isinstance(obj, dict) else None
    if not isinstance(items, list):
        return None
    clean = []
    for it in items[:5]:
        if not isinstance(it, dict) or not str(it.get("title", "")).strip():
            continue
        clean.append({"title": str(it["title"])[:200], "action": str(it.get("action", ""))[:500],
                      "reason": str(it.get("reason", ""))[:500],
                      "confidence": it.get("confidence") if it.get("confidence") in ("Baja", "Media") else "Baja",
                      "refs": [str(r) for r in (it.get("refs") or [])][:6],
                      "evidence": it.get("evidence") if isinstance(it.get("evidence"), dict) else {}})
    return {"source": str(obj.get("source", ""))[:200], "generatedAt": obj.get("generatedAt"),
            "adsLastSync": obj.get("adsLastSync"), "detailDays": obj.get("detailDays"),
            "rejected": len(obj.get("rejected") or []), "suggestions": clean}


def num(s):
    s = s.replace("%", "").replace("+", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return None


def read_keywords(csv_path):
    raw = Path(csv_path).read_bytes()
    txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(txt), delimiter="\t"))
    hi = next(i for i, r in enumerate(rows) if r and r[0].strip().lower() == "keyword")
    ix = {n: i for i, n in enumerate(rows[hi])}

    def g(r, n):
        return r[ix[n]].strip() if n in ix and ix[n] < len(r) else ""

    out = []
    for r in rows[hi + 1:]:
        if not r or not r[0].strip():
            continue
        out.append({
            "k": g(r, "Keyword"),
            "v": int(num(g(r, "Avg. monthly searches")) or 0),
            "c": g(r, "Competition"),
            "lo": int(num(g(r, "Top of page bid (low range)")) or 0),
            "hi": int(num(g(r, "Top of page bid (high range)")) or 0),
            "yoy": g(r, "Cambio interanual"),
        })
    return out


def find_node_env():
    env = dict(os.environ)
    portable = Path(r"E:\nodejs-portable")
    if portable.exists():
        env["PATH"] = str(portable) + os.pathsep + env["PATH"]
    return env


def tailwind_css(env):
    exe = TOOL / "node_modules" / ".bin" / ("tailwindcss.cmd" if os.name == "nt" else "tailwindcss")
    if not exe.exists():
        npm = shutil.which("npm", path=env["PATH"])
        if not npm:
            sys.exit("Falta Node.js/npm para compilar el CSS.")
        print("Instalando Tailwind (una sola vez)...")
        subprocess.run([npm, "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=TOOL, env=env, check=True)
    r = subprocess.run([str(exe), "-c", "tw.config.js", "-i", "input.css", "-o", ".build/out.css", "--minify"],
                       cwd=TOOL, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Tailwind falló:\n" + r.stderr[-800:])
    return read_text(BUILD / "out.css")


def check_js_syntax(scripts, env):
    """Falla el armado si algun script de la pagina tiene un error de sintaxis (evita publicar un panel roto)."""
    import tempfile
    node = shutil.which("node", path=env["PATH"])
    if not node:
        print("AVISO: no hay Node para revisar la sintaxis del script.")
        return
    for js in scripts:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(js); path = f.name
        r = subprocess.run([node, "--check", path], capture_output=True, text=True)
        os.unlink(path)
        if r.returncode != 0:
            sys.exit("ERROR DE SINTAXIS en el script del panel; no se escribió nada:" + LF_ + r.stderr[:700])


LF_ = chr(10)
ENC_FILE = DATA / "panel_data.enc.json"
KEY_FILE = Path(r"E:\config\ubertransfer_panel_key.dpapi")
CLOUD_MARK = "/* ===== Acceso privado y nube"
BOOT_JS = """async function cloudBoot(db){if(window.__APPBOOT)return;
 const ks=await db.collection("panel").doc("clave").get();
 if(!ks.exists)throw new Error("clave-no-provisionada");
 const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
 let pt;try{const key=await crypto.subtle.importKey("raw",b64(ks.data().k),"AES-GCM",false,["decrypt"]);pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(ENC.iv)},key,b64(ENC.ct))}catch(e){throw new Error("descifrado-fallido")}
 window.__SECRET=JSON.parse(new TextDecoder().decode(pt));
 const x=document.createElement("script");x.textContent=document.getElementById("appsrc").textContent;document.head.appendChild(x);window.__APPBOOT=true}"""

NODE_ENC = "const c=require('crypto');let d='';process.stdin.on('data',x=>d+=x).on('end',()=>{const o=JSON.parse(d);const iv=c.randomBytes(12);const ci=c.createCipheriv('aes-256-gcm',Buffer.from(o.key,'base64'),iv);const ct=Buffer.concat([ci.update(o.pt,'utf8'),ci.final(),ci.getAuthTag()]);process.stdout.write(JSON.stringify({iv:iv.toString('base64'),ct:ct.toString('base64')}))})"
NODE_DEC = "const c=require('crypto');let d='';process.stdin.on('data',x=>d+=x).on('end',()=>{const o=JSON.parse(d);const ct=Buffer.from(o.ct,'base64');const de=c.createDecipheriv('aes-256-gcm',Buffer.from(o.key,'base64'),Buffer.from(o.iv,'base64'));de.setAuthTag(ct.subarray(ct.length-16));process.stdout.write(Buffer.concat([de.update(ct.subarray(0,ct.length-16)),de.final()]))})"


def get_key():
    """Clave AES (base64, 32 bytes): variable PANEL_DATA_KEY o archivo DPAPI en E:\\config. None si no hay."""
    k = os.environ.get("PANEL_DATA_KEY", "").strip()
    if k:
        return k
    if os.name == "nt" and KEY_FILE.exists():
        ps = ("$t=(Get-Content -Raw -LiteralPath '%s').Trim();$s=ConvertTo-SecureString $t;"
              "[Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))" % KEY_FILE)
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


def node_run(script, payload, env):
    node = shutil.which("node", path=env["PATH"])
    if not node:
        sys.exit("Hace falta Node.js para cifrar/verificar los datos del panel.")
    r = subprocess.run([node, "-e", script], input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit("Fallo de Node al cifrar/descifrar: " + r.stderr[:300])
    return r.stdout


def make_enc(secret_json, env, enc_file=None):
    """Devuelve el bloque cifrado {inputsSha, iv, ct}. Con clave: cifra (o reutiliza si las entradas no cambiaron).
    Sin clave (p. ej. GitHub Actions): reutiliza data/panel_data.enc.json solo si coincide con las entradas actuales."""
    inputs_sha = hashlib.sha256(secret_json.encode("utf-8")).hexdigest()
    enc_file = enc_file or ENC_FILE
    cur = json.loads(read_text(enc_file)) if enc_file.exists() else None
    if cur and cur.get("inputsSha") == inputs_sha:
        print(f"Cifrado: se reutiliza {enc_file.name} (las entradas no cambiaron).")
        return cur
    key = get_key()
    if not key:
        sys.exit("Las entradas (frases/previsión/tendencias) cambiaron y no hay clave para cifrarlas. "
                 "Arma el panel en el PC del dueño (clave en E:\\config) y sube data/panel_data.enc.json.")
    out = json.loads(node_run(NODE_ENC, {"key": key, "pt": secret_json}, env))
    back = node_run(NODE_DEC, {"key": key, "iv": out["iv"], "ct": out["ct"]}, env)
    if back != secret_json:
        sys.exit("El cifrado no se puede descifrar de vuelta; no se escribió nada.")
    enc = {"v": 1, "alg": "AES-256-GCM", "inputsSha": inputs_sha, "iv": out["iv"], "ct": out["ct"]}
    enc_file.write_text(json.dumps(enc), encoding="utf-8")
    print("Cifrado: datos nuevos cifrados y verificados (descifrado de vuelta OK).")
    return enc


def split_encrypted(page_tpl, enc, pub):
    """Del HTML con marcadores saca la version publicada: script de acceso + codigo de la app como texto inerte."""
    i = page_tpl.index("<script>") + len("<script>")
    j = page_tpl.rindex("</script>")
    js = page_tpl[i:j]
    k = js.index(CLOUD_MARK)
    app, gate = js[:k], js[k:]
    a = app.replace("const DATA=__DATA__;", "const DATA=__SECRET.data;").replace(
        "const META=__META__;", "const META=Object.assign({},__PUB,__SECRET.meta);")
    assert "__DATA__" not in a and "__META__" not in a, "no se encontraron los marcadores de datos"
    g0 = gate.index("/*BOOT*/"); g1 = gate.index("/*ENDBOOT*/") + len("/*ENDBOOT*/")
    gate = gate[:g0] + BOOT_JS + gate[g1:]
    pre = "const ENC=" + json.dumps({"iv": enc["iv"], "ct": enc["ct"]}) + ";const __PUB=" + json.dumps(pub, ensure_ascii=False, separators=(",", ":")) + ";" + LF_
    gate = pre + gate
    for name, code in (("app", a), ("acceso", gate)):
        assert "</script" not in code.lower(), "texto '</script' dentro del codigo (" + name + ")"
    assert "<!--" not in a, "'<!--' dentro del codigo de la app"
    html = page_tpl[:i - len("<script>")] + "<script>" + gate + "</script>" + LF_ + '<script type="text/plain" id="appsrc">' + a + "</script>" + page_tpl[j + len("</script>"):]
    return html, a, gate


def read_ampliacion():
    """Frases de otros rubros (corporativo, bodas...) capturadas del Planificador: data/keyword_planner_rubros_*.json.
    Entran al panel como 'ampliación' (no cuentan entre las frases del archivo de Google). Volumen: 10-100 -> 50, 100-1 mil -> 500."""
    files = sorted(DATA.glob("keyword_planner_rubros_*.json"))
    if not files:
        return []
    d = json.loads(read_text(files[-1]))
    vol = {"10-100": 50, "100-1 mil": 500}
    by = {r["k"]: r for r in d["filas"]}
    out = []
    for k in d["panel"]:
        r = by[k]
        out.append({"k": k, "v": vol.get(r["rango"], 0), "rango": r["rango"].replace("-", "–"), "c": r["competencia"],
                    "lo": r["puja_baja_clp"], "hi": r["puja_alta_clp"], "dueno": k in d["semillas_dueno"]})
    return out



AE_CH = [
    "Auditoría técnica de aereostar.cl: PENDIENTE (aún no se ejecuta; hacerla desde GitHub con el flujo manual, no desde este PC, para no bloquear el sitio del cliente)",
    "Flota: la página /nuestra-flota muestra Kia Sorento, Kia Gran Carnival, Mercedes Vito y Kia Sonata con «6 pasajeros, Van, 2020» para los cuatro (la Sonata no es van): revisar esos datos",
    "Confirmar el teléfono/WhatsApp de Aereostar y si es distinto del de UberTransfer; definir cuál va en los anuncios (PENDIENTE Rafael)",
    "Tarifas y horarios de Aereostar: sin datos verificados (PENDIENTE Rafael)",
    "Verificar etiquetas de medición (GA4/GTM) propias de aereostar.cl y los eventos click_whatsapp, click_phone y lead_submit",
    "Marca: «Aereostar» no figura registrada en INAPI (consulta pública 30-09-2026); consultar a un abogado de propiedad industrial sobre registrarla en clase 39 (transporte)",
    "Coordinar con UberTransfer: una frase, un dueño (ver consultas/01_coordinacion_aereostar_ubertransfer/05_sintesis.md en el repositorio)",
    "Conseguir el historial de la campaña de Búsqueda «Aereostar Octubre 2025» (términos de búsqueda, costo, clics, conversiones) para medir esta marca por separado",
]
AE_BIZ = ["Teléfono/WhatsApp, horario y tarifas de Aereostar: sin datos verificados (PENDIENTE Rafael)", "Historial de la campaña «Aereostar Octubre 2025» (clics, costo, conversiones): pedirlo a Rafael o a quien la administra", "Marca «Aereostar»: no figura registrada en INAPI (30-09-2026); falta la opinión de un abogado de propiedad industrial", "Flota real y capacidades: la página muestra «6 pasajeros, Van, 2020» para los cuatro vehículos (dudoso)", "Coordinación con UberTransfer (una frase, un dueño): falta la decisión de Rafael sobre quién lleva el aeropuerto", "Conversiones reales (WhatsApp, teléfono, correo): sin medir", "Search Console y GA4: sin datos reales conectados"]
AE_GUIA = ('<div class="card warn"><h2>Este es el panel de Aereostar</h2><p>Está <b>separado del panel de UberTransfer</b> para no mezclar datos: '
           'las marcas, notas y el historial de consultas de aquí son solo de Aereostar. Las cifras reales vienen de su propia cuenta de Google Ads '
           '(548-530-8262), siempre <b>solo en lectura</b>: el panel no crea, pausa ni cambia campañas, presupuestos ni anuncios. '
           'Las frases, la previsión y las tendencias de Google son del mercado de aeropuerto y se comparten como referencia.</p></div>')


def ae_checklist(au):
    """Lista de mejoras de Aereostar: si hay auditoría real (data/audit_aereostar_latest.json) se suman sus hallazgos,
    agrupando los que se repiten en varias páginas."""
    import re as _re
    if not au.get("generated"):
        return AE_CH
    pages = au["pages"]
    grupos = {}
    for p in pages:
        path = p["url"].replace("https://aereostar.cl", "") or "/"
        for iss in p["issues"]:
            clave = _re.sub(r"^\d+ ", "", _re.sub(r"\s*\(.*?\)", "", iss)).strip()
            g = grupos.setdefault(clave, {"ejemplo": iss, "paginas": []})
            g["paginas"].append(path)
    items = [f"Auditoría técnica de aereostar.cl ejecutada el {au['generated'][:10]} ({len(pages)} páginas, solo lectura, 3 s entre páginas): hallazgos agrupados a continuación"]
    for clave, g in sorted(grupos.items(), key=lambda kv: -len(kv[1]["paginas"])):
        n = len(g["paginas"])
        ej = ", ".join(g["paginas"][:3]) + (" …" if n > 3 else "")
        items.append(f"{clave or g['ejemplo']}: {n} de {len(pages)} páginas (ejemplo: {g['ejemplo']}; {ej})")
    if len(items) == 1:
        items.append("Sin hallazgos en las páginas revisadas")
    tema = [p["url"].replace("https://aereostar.cl", "") for p in pages if "woodmart_slider" in p["url"] or p["url"].rstrip("/").endswith(("/portfolio", "/compare"))]
    if tema:
        items.append("El sitemap incluye páginas que parecen de la plantilla del tema (" + ", ".join(tema) + "): revisar si deben indexarse o quitarse (interpretación a confirmar con Rafael)")
    if pages and all(p["status"] == 200 for p in pages):
        rap = sorted(p["seconds"] for p in pages)
        items.append(f"Velocidad: todas las páginas respondieron 200; tiempos de {rap[0]} a {rap[-1]} s (buen punto de partida; UberTransfer tarda más)")
    return items + AE_CH[1:]


UT_COLORS = (("#1d4ed8", "#b90f16"), ("#1a73e8", "#ed1c24"), ("#2563eb", "#ed1c24"), ("#3b82f6", "#f0484e"),
             ("37,99,235", "237,28,36"), ("37 99 235", "237 28 36"))


# Fondo fotográfico sutil de Aereostar: cubierta y cielo del aeropuerto (foto del dueño, sin logos ni textos)
AE_BG = ':root{--bg-img:url("/bg/aereostar-fondo.jpg");--bg-op:.62}'
# Fondo fotográfico sutil de UberTransfer (foto del dueño, recortada y comprimida en site/bg/); Aereostar no lo lleva hasta tener sus fotos
UT_BG = ':root{--bg-img:url("/bg/ubertransfer-fondo.jpg")}'


def ut_recolor(text):
    """Pasa los azules de la plantilla al rojo del logo de UberTransfer (el panel usa solo los colores de su marca)."""
    for o, n in UT_COLORS:
        text = text.replace(o, n)
    return text


AE_COLORS = (("#1d4ed8", "#b84a08"), ("#1a73e8", "#e96712"), ("#2563eb", "#e96712"), ("#3b82f6", "#f29812"),
             ("37,99,235", "233,103,18"), ("37 99 235", "233 103 18"),
             ("#ed1c24", "#e96712"), ("#b90f16", "#b84a08"), ("#b3121a", "#b84a08"), ("237,28,36", "233,103,18"),
             ("#f3a0a4", "#f8c9a0"), ("#f3c4c6", "#f8d3b0"), ("#f3b4b7", "#f8c9a0"), ("#fff4f4", "#fff4ea"),
             ("#58b947", "#f8e71d"), ("#6ab04c", "#f8e71d"), ("#111318", "#0b0b0b"))


def ae_recolor(text):
    """Pasa los azules de la plantilla al naranja del logo de Aereostar (solo se usa en el panel de Aereostar)."""
    for o, n in AE_COLORS:
        text = text.replace(o, n)
    return text


def brand_aereostar(page, ch=None):
    """Convierte la plantilla (hecha para UberTransfer) en la del panel de Aereostar."""
    # App instalable (PWA): Aereostar tiene la suya, con su manifiesto, su service worker y sus íconos bajo /aereostar/
    ico = re.search(r"<!--AEICON(.*?)AEICON-->", page, flags=re.S)
    assert ico, "aereostar: no se encontró el favicon guardado"
    page = page.replace(ico.group(0), "")          # el favicon SVG de UberTransfer no se usa: va el PNG del logo
    pwa = re.search(r"<!--PWA-->.*?<!--/PWA-->", page, flags=re.S)
    assert pwa, "aereostar: no se encontró el bloque PWA"
    blk = pwa.group(0)
    for o, n in (("/manifest.webmanifest", "/aereostar/manifest.webmanifest"),
                 ('register("/sw.js")', 'register("/aereostar/sw.js",{scope:"/aereostar/"})'),
                 ('content="#ed1c24"', 'content="#0b0b0b"')):
        assert blk.count(o) == 1, ("aereostar PWA: no se encontró " + o)
        blk = blk.replace(o, n)
    page = page.replace(pwa.group(0), blk)
    page = page.replace("/icons/", "/aereostar/icons/")   # logo, favicon, apple-touch y el aviso de actualización
    def one(s, o, n):
        assert s.count(o) == 1, ("aereostar: no se encontró exactamente una vez: " + o[:60], s.count(o))
        return s.replace(o, n)
    # lista de mejoras propia (se aparta antes de los reemplazos globales)
    i = page.index("const CH=["); j = page.index('"];', i) + 3
    page = page[:i] + "const CH=__CH_AE__;" + page[j:]
    page = page.replace("UberTransfer", "Aereostar").replace("ubertransfer.cl", "aereostar.cl")
    page = one(page, "<section id=\"guia\">", "<section id=\"guia\">" + AE_GUIA)
    page = one(page, 'href="/aereostar/" class="inline-flex', 'href="/" class="inline-flex')
    page = one(page, ">Panel Aereostar →</a>", ">← Panel UberTransfer</a>")
    i = page.index("const BIZ=window.__BIZ=["); j = page.index("];", i) + 2
    page = page[:i] + "const BIZ=window.__BIZ=" + json.dumps(AE_BIZ, ensure_ascii=False) + ";" + page[j:]
    page = ae_recolor(page)
    assert "#ed1c24" not in page and "#2563eb" not in page, "aereostar: quedaron colores de UberTransfer"
    page = one(page, '<span class="material-symbols-outlined text-white">flight_takeoff</span>',
               '<img src="/aereostar/icons/logo-128.png" alt="Logo Aereostar" width="32" height="32" style="border-radius:50%;display:block">')
    assert "/aereostar/icons/favicon-32.png" in page and "/aereostar/manifest.webmanifest" in page, "aereostar: faltan el favicon o el manifiesto"
    page = one(page, 'const SUGDOC="aiSuggestions"', 'const SUGDOC="aiSuggestions_aereostar"')   # sus recomendaciones, no las de UberTransfer
    page = one(page, 'const KP="";', 'const KP="ae_";')
    page = one(page, 'const MYB="ubertransfer";', 'const MYB="aereostar";')
    page = one(page, '.doc("estado")', '.doc("estado_aereostar")')
    page = one(page, "el sitio tiene WhatsApp y teléfono: <b>+56 9 4996 9267</b>, dato verificado", "teléfono/WhatsApp de Aereostar: <b>PENDIENTE de confirmar</b>, sin verificar")
    page = page.replace("+56 9 4996 9267", "teléfono de Aereostar: PENDIENTE")
    page = one(page, "el flujo «SEO diario» <b>no está extrayendo datos</b>", "Aereostar aún no tiene extracción de datos")
    page = page.replace("__CH_AE__", json.dumps(ch or AE_CH, ensure_ascii=False))
    assert "4996" not in page, "quedó el teléfono de UberTransfer en el panel de Aereostar"
    return page


def main():
    BUILD.mkdir(exist_ok=True)
    csv_path = sorted(DATA.glob("keyword_planner_*.csv"))[-1]
    src_meta = json.loads(read_text(csv_path.with_suffix(".meta.json")))
    rows = read_keywords(csv_path)
    if len(rows) != src_meta["rows"]:
        sys.exit(f"Inconsistencia: el CSV tiene {len(rows)} filas y Google mostraba {src_meta['rows']}.")
    data_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))   # igual que JSON.stringify en el navegador
    data_sha = hashlib.sha256(data_json.encode("utf-8")).hexdigest()
    src_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    aud = json.loads(read_text(DATA / "audit_latest.json"))
    audit = {"generated": aud["generated"],
             "pages": [{"url": p["url"], "status": p["status"], "seconds": p["seconds"], "issues": p["issues"]}
                       for p in aud["pages"]]}
    fc = json.loads(read_text(DATA / "forecast_google.json"))
    forecast = {k: fc[k] for k in ("planId", "generatedAt", "period", "strategy", "clicks", "impressions",
                                   "cost", "ctr", "cpc", "dailyBudget", "keywords")}
    tr = json.loads(read_text(DATA / "trends_estacionalidad.json"))
    seo_f = DATA / "seo_status.json"
    seo_status = json.loads(read_text(seo_f)) if seo_f.exists() else {"state": "sin_ejecutar", "missing": []}
    google_ads = read_google_ads_status(DATA / "google_ads_ubertransfer.json", "UberTransfer")
    google_ads["aiSuggestions"] = read_ai_suggestions(DATA / "ai_suggestions_latest.json")
    aereostar_ads = read_google_ads_status(DATA / "google_ads_aereostar.json", "Aereostar", ("24331409273",))
    aereostar_ads["aiSuggestions"] = read_ai_suggestions(DATA / "ai_suggestions_aereostar_latest.json")
    assert len(tr["indice_mensual"]) == 12, "Trends: faltan meses"
    meta = {
        "srcName": src_meta["srcName"], "srcSha": src_sha, "srcRows": src_meta["rows"],
        "dataSha": data_sha, "exportedAt": src_meta["exportedAt"],
        "builtAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "audit": audit, "forecast": forecast, "trends": tr, "plannerActive": False, "seoStatus": seo_status,
        "googleAds": google_ads,
    }

    meta["ampliacion"] = read_ampliacion()
    ae_f = DATA / "audit_aereostar_latest.json"
    ae_audit = {"generated": None, "pages": []}
    if ae_f.exists():
        a = json.loads(read_text(ae_f))
        ae_audit = {"generated": a["generated"],
                    "pages": [{"url": p["url"], "status": p["status"], "seconds": p["seconds"], "issues": p["issues"]} for p in a["pages"]]}
    ae_ch = ae_checklist(ae_audit)
    ae_tf = lambda p: brand_aereostar(p, ae_ch)
    env = find_node_env()
    # Tailwind genera solo las clases que aparecen en estos archivos: se escriben las DOS plantillas (sin datos) antes de compilar el CSS
    for old in BUILD.glob("*.html"):
        old.unlink()
    for nm, tpl in (("ubertransfer", None), ("aereostar", ae_tf)):
        src = read_text(TOOL / "template.html")
        src = (src if tpl is None else tpl(src)).replace("<!--IAS-->", read_text(TOOL / ("ias.html" if tpl is None else "ias_aereostar.html")))
        (BUILD / f"page_{nm}.html").write_text(src.replace("__DATA__", "[]").replace("__META__", "{}").replace("__CSS__", ""), encoding="utf-8")
    css = tailwind_css(env) + read_text(TOOL / "extra.css")
    assert len(css) > 20000, f"el CSS de Tailwind salió demasiado chico ({len(css)} bytes): faltan clases; no se publica"
    SECRET_KEYS = ("srcName", "srcSha", "srcRows", "dataSha", "exportedAt", "forecast", "trends", "ampliacion", "googleAds")
    import re as _re
    VARIANTS = [
        {"name": "UberTransfer", "ias": "ias.html", "transform": ut_recolor, "enc": ENC_FILE, "meta": meta,
         "site": ROOT / "site", "docs": ROOT / "docs" / "panel_keywords.html"},
        {"name": "Aereostar", "ias": "ias_aereostar.html", "transform": ae_tf, "enc": DATA / "panel_data_aereostar.enc.json",
         "meta": dict(meta, ampliacion=[], audit=ae_audit, forecast=forecast, trends=tr, plannerActive=True, fullMenu=True, googleAds=aereostar_ads), "site": ROOT / "site" / "aereostar",
         "docs": ROOT / "docs" / "panel_aereostar.html"},
    ]
    resumen = []
    for V in VARIANTS:
        m = V["meta"]
        page_tpl = V["transform"](read_text(TOOL / "template.html")).replace("<!--IAS-->", read_text(TOOL / V["ias"]))
        plain = page_tpl.replace("__DATA__", data_json).replace("__META__", json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        secret_json = json.dumps({"data": rows, "meta": {k: m[k] for k in SECRET_KEYS}}, ensure_ascii=False, separators=(",", ":"))
        assert json.dumps(json.loads(secret_json)["data"], ensure_ascii=False, separators=(",", ":")) == data_json, \
            "el cifrado altera el orden/formato de las filas: la huella SHA-256 no coincidiría"
        pub = {k: m[k] for k in ("builtAt", "audit", "seoStatus", "plannerActive", "fullMenu") if k in m}
        enc = make_enc(secret_json, env, V["enc"])
        pub_html, app_js, gate_js = split_encrypted(page_tpl, enc, pub)
        vcss = ae_recolor(css) + AE_BG if V["name"] == "Aereostar" else ut_recolor(css) + UT_BG
        final_plain = plain.replace("__CSS__", vcss)
        final_pub = pub_html.replace("__CSS__", vcss)
        assert "__DATA__" not in final_plain and "__META__" not in final_plain and "__CSS__" not in final_plain
        assert "__CSS__" not in final_pub and "__DATA__" not in final_pub.replace("__SECRET", "")
        who = V["name"]
        assert '"yoy"' not in final_pub and data_json[:200] not in final_pub, f"las filas de Google quedaron en claro ({who})"
        assert '"planId"' not in final_pub and '"indice_mensual"' not in final_pub and "1441122025" not in final_pub, f"previsión/tendencias en claro ({who})"
        plain_scripts = _re.findall(r"<script>(.*?)</script>", final_plain, _re.S)
        check_js_syntax([max(plain_scripts, key=len), app_js, gate_js], env)
        V["docs"].write_text(final_plain, encoding="utf-8")                      # solo local, en claro
        V["site"].mkdir(parents=True, exist_ok=True)
        (V["site"] / "index.html").write_text(final_pub, encoding="utf-8")       # publicado: datos cifrados
        ver = {"dataSha": data_sha, "builtAt": m["builtAt"], "exportedAt": m["exportedAt"],
               "auditGenerated": m["audit"]["generated"], "srcSha": src_sha}
        (V["site"] / "version.json").write_text(json.dumps(ver, ensure_ascii=False), encoding="utf-8")
        resumen.append(f"{who}: publicado {len(final_pub)} bytes (cifrado), copia local {len(final_plain)} bytes")
    print(f"OK: {len(rows)} frases · datos {data_sha[:12]} · auditoría {audit['generated']} · " + " | ".join(resumen))


if __name__ == "__main__":
    main()
