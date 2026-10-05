"""Auditoría técnica: recorre el sitemap y revisa cada URL. Solo lectura."""
import json
import re
import time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import requests

UA = {"User-Agent": "MarcasTransporteOpsAudit/1.0 (+auditoria interna)"}
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
MAX_TITLE = 60
MAX_DESC = 160


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1 = 0
        self.imgs = 0
        self.imgs_no_alt = 0
        self.imgs_lazy = 0
        self.meta_desc = None
        self.canonical = None
        self.hreflang = []
        self.jsonld = []
        self._in_jsonld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            self.imgs += 1
            if "alt" not in a:  # alt="" es válido (imagen decorativa)
                self.imgs_no_alt += 1
            if a.get("loading") == "lazy":
                self.imgs_lazy += 1
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.meta_desc = (a.get("content") or "").strip()
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if rel == "canonical":
                self.canonical = a.get("href")
            elif rel == "alternate" and a.get("hreflang"):
                self.hreflang.append(a["hreflang"])
        elif tag == "script" and (a.get("type") or "") == "application/ld+json":
            self._in_jsonld = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append("".join(self._buf))

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_jsonld:
            self._buf.append(data)


def analyze_html(html: str) -> dict:
    """Extrae señales SEO de un HTML. Función pura (testeable sin red)."""
    p = _Page()
    p.feed(html)
    bad_jsonld = 0
    for raw in p.jsonld:
        try:
            json.loads(raw)
        except ValueError:
            bad_jsonld += 1
    return {
        "title": p.title.strip(),
        "meta_description": p.meta_desc,
        "h1_count": p.h1,
        "canonical": p.canonical,
        "hreflang": p.hreflang,
        "images": p.imgs,
        "images_no_alt": p.imgs_no_alt,
        "images_lazy": p.imgs_lazy,
        "jsonld_blocks": len(p.jsonld),
        "jsonld_invalid": bad_jsonld,
        "html_bytes": len(html.encode("utf-8")),
    }


def issues_for(url: str, status: int, seconds: float, info: dict | None) -> list[str]:
    """Convierte las señales de una página en problemas concretos."""
    if status >= 400 or status == 0:
        return [f"HTTP {status or 'sin respuesta'}"]
    out = []
    if info is None:
        return out
    if not info["title"]:
        out.append("falta <title>")
    elif len(info["title"]) > MAX_TITLE + 10:
        out.append(f"title largo ({len(info['title'])} car.)")
    if not info["meta_description"]:
        out.append("falta meta description")
    elif len(info["meta_description"]) > MAX_DESC + 20:
        out.append(f"description larga ({len(info['meta_description'])} car.)")
    if info["h1_count"] != 1:
        out.append(f"H1 = {info['h1_count']} (debe ser 1)")
    if not info["canonical"]:
        out.append("falta canonical")
    if info["images_no_alt"]:
        out.append(f"{info['images_no_alt']} imágenes sin alt")
    if info["images"] >= 10 and info["images_lazy"] == 0:
        out.append(f"{info['images']} imágenes sin lazy-load")
    if info["jsonld_invalid"]:
        out.append("JSON-LD inválido")
    if seconds > 3.0:
        out.append(f"respuesta lenta ({seconds:.1f}s)")
    return out


def parse_sitemap(xml_text: str) -> tuple[list[str], list[str]]:
    """Devuelve (sitemaps_hijos, urls) de un sitemap o índice."""
    root = ET.fromstring(xml_text)
    locs = [e.text.strip() for e in root.iter(f"{NS}loc") if e.text]
    if root.tag == f"{NS}sitemapindex":
        return locs, []
    return [], locs


class AuditError(RuntimeError):
    """La auditoría no pudo ejecutarse (distinto de «se ejecutó y encontró problemas»)."""


def collect_urls(site_url: str, session, depth: int = 0, report: dict | None = None) -> list[str]:
    """Descubre URLs desde robots.txt → sitemap. Ignora recursos no HTML.

    Si se pasa `report`, deja ahí el estado de robots.txt y de cada sitemap (para que un
    fallo de descubrimiento no parezca una auditoría exitosa).
    """
    report = report if report is not None else {}
    report.update({"robots": None, "sitemaps": []})
    try:
        rr = session.get(f"{site_url}/robots.txt", headers=UA, timeout=20)
        report["robots"] = rr.status_code
        robots = rr.text if rr.status_code < 400 else ""
    except requests.RequestException as e:
        report["robots"] = f"error: {type(e).__name__}"
        robots = ""
    maps = re.findall(r"(?im)^sitemap:\s*(\S+)", robots) or [f"{site_url}/sitemap_index.xml"]
    urls, queue, seen = [], list(maps), set()
    while queue and len(seen) < 30:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        try:
            r = session.get(sm, headers=UA, timeout=20)
            children, page_urls = parse_sitemap(r.text)
            report["sitemaps"].append({"url": sm, "status": r.status_code, "urls": len(page_urls), "children": len(children)})
        except (requests.RequestException, ET.ParseError) as e:
            report["sitemaps"].append({"url": sm, "status": f"error: {type(e).__name__}", "urls": 0, "children": 0})
            continue
        queue.extend(children)
        urls.extend(u for u in page_urls if not u.endswith((".kml", ".xml", ".jpg", ".png", ".webp")))
    return list(dict.fromkeys(urls))


def run(site_url: str, session=None, delay: float = 0.0, max_urls: int = 0) -> dict:
    s = session or requests.Session()
    result = {"site": site_url, "pages": [], "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    discovery: dict = {}
    urls = collect_urls(site_url, s, report=discovery)
    result["discovery"] = discovery
    if not urls:
        raise AuditError("No se descubrió ninguna URL (robots.txt/sitemap inaccesible o vacío): "
                         f"robots={discovery.get('robots')}, sitemaps={discovery.get('sitemaps')}")
    if max_urls:
        urls = urls[:max_urls]
    for n, url in enumerate(urls):
        if delay and n:
            time.sleep(delay)
        t0 = time.time()
        status, info = 0, None
        try:
            r = s.get(url, headers=UA, timeout=30)
            status = r.status_code
            if status < 400:
                info = analyze_html(r.text)
        except requests.RequestException:
            pass
        secs = time.time() - t0
        result["pages"].append({"url": url, "status": status, "seconds": round(secs, 2),
                                "issues": issues_for(url, status, secs, info), "info": info})
    return result
