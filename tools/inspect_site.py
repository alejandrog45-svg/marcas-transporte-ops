#!/usr/bin/env python3
"""Inspección de contenido del sitio (solo lectura, 4 solicitudes normales).

Verifica con evidencia las afirmaciones que hicieron ChatGPT, Gemini y Meta AI sobre el HTML del sitio.
Escribe data/inspeccion_sitio_latest.json. No usa rutas de escáner ni sondea archivos sensibles.
"""
import json, os, re, time, urllib.request, collections
from html.parser import HTMLParser

BASE = os.environ.get("SITE_URL", "https://ubertransfer.cl").rstrip("/")
PAGES = ["/", "/nosotros-transfer-aeropuerto-santiago/", "/servicio-transfer-aeropuerto-santiago/", "/contacto-transfer-aeropuerto-santiago/"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; marcas-transporte-ops-inspeccion; lectura)", "Accept-Language": "es-CL,es;q=0.9"}


def fetch(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        return r.status, body.decode("utf-8", "ignore"), time.time() - t0, dict(r.headers)


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self._in_title = False
        self.meta = {}; self.links = []; self.imgs = []; self.scripts = []; self.hrefs = []
        self.heads = collections.defaultdict(list); self._head = None; self._buf = ""
        self.jsonld = []; self._in_ld = False; self._ld = ""
        self.forms = 0; self.iframes = 0; self.nav_hrefs = []; self._nav = 0; self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self._in_title = True
        if tag == "meta":
            k = a.get("name") or a.get("property") or a.get("http-equiv")
            if k: self.meta[k.lower()] = a.get("content", "")
        if tag == "link": self.links.append(a)
        if tag == "img": self.imgs.append(a)
        if tag == "script":
            if a.get("src"): self.scripts.append(a["src"])
            if a.get("type") == "application/ld+json": self._in_ld = True; self._ld = ""
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
            if self._nav: self.nav_hrefs.append(a["href"])
        if tag == "nav": self._nav += 1
        if tag == "form": self.forms += 1
        if tag == "iframe": self.iframes += 1
        if tag in ("h1", "h2", "h3"): self._head = tag; self._buf = ""

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False
        if tag == "nav" and self._nav: self._nav -= 1
        if tag == "script" and self._in_ld:
            self._in_ld = False
            try: self.jsonld.append(json.loads(self._ld))
            except Exception: self.jsonld.append({"_error": "JSON-LD invalido"})
        if tag == self._head:
            txt = re.sub(r"\s+", " ", self._buf).strip()
            if txt: self.heads[tag].append(txt)
            self._head = None

    def handle_data(self, d):
        if self._in_title: self.title += d
        if self._in_ld: self._ld += d
        if self._head: self._buf += d


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            out.append((k, v)); walk(v, out)
    elif isinstance(o, list):
        for i in o: walk(i, out)


def ctx(text, pat, n=50, maxn=4):
    res = []
    for m in re.finditer(pat, text, re.I):
        s = max(0, m.start() - n); e = min(len(text), m.end() + n)
        res.append(re.sub(r"\s+", " ", text[s:e]))
        if len(res) >= maxn: break
    return res


def strip_tags(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))


def analyze(path):
    try:
        st, html, dt, hdr = fetch(path)
    except Exception as e:
        return {"path": path, "error": str(e)}
    p = P(); p.feed(html)
    text = strip_tags(html)
    imgs = p.imgs
    ext = collections.Counter()
    for i in imgs:
        u = (i.get("data-src") or i.get("src") or "").split("?")[0]
        ext[u.rsplit(".", 1)[-1].lower() if "." in u else "sin-ext"] += 1
    ld = []; walk(p.jsonld, ld)
    types = sorted({str(v) if not isinstance(v, list) else ",".join(map(str, v)) for k, v in ld if k == "@type"})
    hours = [(k, v) for k, v in ld if k in ("openingHours", "openingHoursSpecification", "openingHoursspecification")]
    tel = [str(v) for k, v in ld if k == "telephone"]
    hosts = collections.Counter(re.sub(r"^(?:https?:)?//([^/]+).*", r"\1", s) for s in p.scripts if s.startswith(("http", "//")))
    plugins = sorted(set(re.findall(r"wp-content/plugins/([a-z0-9\-_]+)", html)))
    dup_heads = [h for h, c in collections.Counter(sum(p.heads.values(), [])).items() if c > 1]
    return {
        "path": path, "status": st, "segundos": round(dt, 2), "bytes_html": len(html.encode("utf-8")),
        "cabeceras": {k: v[:80] for k, v in hdr.items() if k.lower() in ("cache-control", "content-encoding", "expires", "server", "x-litespeed-cache", "x-powered-by", "vary", "strict-transport-security", "x-frame-options", "x-content-type-options", "content-security-policy", "referrer-policy")},
        "lang": p.lang, "title": p.title.strip(), "title_len": len(p.title.strip()),
        "meta_description": p.meta.get("description", ""), "meta_description_len": len(p.meta.get("description", "")),
        "robots_meta": p.meta.get("robots"), "viewport": p.meta.get("viewport"),
        "canonical": [l.get("href") for l in p.links if l.get("rel") in ("canonical", ["canonical"])],
        "hreflang": [l.get("hreflang") for l in p.links if l.get("hreflang")],
        "og": sorted(k for k in p.meta if k.startswith("og:")), "twitter": sorted(k for k in p.meta if k.startswith("twitter:")),
        "h1": p.heads["h1"], "h2": p.heads["h2"][:20], "h3_cantidad": len(p.heads["h3"]), "encabezados_repetidos": dup_heads[:10],
        "imagenes": {"total": len(imgs), "formatos": dict(ext), "con_lazy": sum(1 for i in imgs if i.get("loading") == "lazy"),
                     "sin_alt": sum(1 for i in imgs if not i.get("alt")), "sin_width_height": sum(1 for i in imgs if not (i.get("width") and i.get("height"))),
                     "con_srcset": sum(1 for i in imgs if i.get("srcset"))},
        "scripts": {"total": len(p.scripts), "hosts_externos": dict(hosts.most_common(8)),
                    "gtm": sorted(set(re.findall(r"GTM-[A-Z0-9]+", html))), "ga4": sorted(set(re.findall(r"\bG-[A-Z0-9]{8,12}\b", html))),
                    "gtag_directo": "googletagmanager.com/gtag/js" in html, "gtm_directo": "googletagmanager.com/gtm.js" in html or "GTM-" in html},
        "plugins_en_html": plugins,
        "jsonld": {"bloques": len(p.jsonld), "tipos": types, "telefono": tel[:3], "horario": [(k, json.dumps(v, ensure_ascii=False)[:200]) for k, v in hours][:4],
                   "tiene_areaServed": any(k == "areaServed" for k, v in ld), "tiene_sameAs": any(k == "sameAs" for k, v in ld), "tiene_address": any(k == "address" for k, v in ld)},
        "enlaces": {"tel": sorted(set(h for h in p.hrefs if h.startswith("tel:")))[:6],
                    "whatsapp": sorted(set(h[:110] for h in p.hrefs if re.search(r"wa\.me|whatsapp\.com", h)))[:6],
                    "mailto": sorted(set(h[:80] for h in p.hrefs if h.startswith("mailto:")))[:4],
                    "tarifas": sorted(set(h for h in p.hrefs if re.search(r"tarifa", h, re.I)))[:6]},
        "formularios": p.forms, "iframes": p.iframes,
        "texto": {
            "precios_visibles": ctx(text, r"\$\s?\d[\d\.]{2,}", 45, 6),
            "horario": ctx(text, r"24 horas|24/7|09:00|17:00|lunes a|horario", 45, 6),
            "marca_partida": ctx(text, r"Tran\s+sfer", 30, 3),
            "qr": ctx(text, r"\bQR\b", 45, 2), "ejecutiva": ctx(text, r"ejecutiva", 45, 2),
            "flota": ctx(text, r"Carnival|Sorento|Kia\b|Mercedes|Hyundai|Toyota", 35, 5),
            "pet": ctx(text, r"pet", 30, 2), "descuento": ctx(text, r"descuento", 45, 3),
            "cotizaciones_correo": ctx(text, r"cotizaciones@", 30, 2), "instagram": ctx(text, r"instagram", 30, 2),
            "pago": ctx(text, r"pago|pagar|transferencia", 40, 4),
        },
    }


def main():
    out = {"generado_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sitio": BASE, "paginas": []}
    for i, path in enumerate(PAGES):
        out["paginas"].append(analyze(path))
        if i < len(PAGES) - 1: time.sleep(3)          # sin ráfagas: 3 s entre solicitudes
    os.makedirs("data", exist_ok=True)
    with open("data/inspeccion_sitio_latest.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("OK", [(p.get("path"), p.get("status") or p.get("error")) for p in out["paginas"]])


if __name__ == "__main__":
    main()
