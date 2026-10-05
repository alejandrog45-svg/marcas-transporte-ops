"""Reglas puras de análisis y alertas (sin red, totalmente testeables)."""


def find_opportunities(rows: list[dict], min_impr: int = 50, pos_lo: float = 8, pos_hi: float = 20) -> list[dict]:
    """Consultas con demanda y posición 8–20: candidatas a mejorar título/contenido.

    `rows` = filas de gsc_query con dimensions ["query","page"].
    Ordena por impresiones (potencial) descendente.
    """
    out = []
    for r in rows:
        if r["impressions"] >= min_impr and pos_lo <= r["position"] <= pos_hi:
            q, page = (r["keys"] + [""])[:2]
            out.append({"query": q, "page": page, "impressions": r["impressions"],
                        "clicks": r["clicks"], "position": round(r["position"], 1)})
    return sorted(out, key=lambda x: x["impressions"], reverse=True)


def audit_alerts(audit: dict) -> list[str]:
    alerts = []
    for p in audit["pages"]:
        if p["status"] == 0 or p["status"] >= 400:
            alerts.append(f"🔴 {p['url']} → {p['issues'][0]}")
    slow = [p for p in audit["pages"] if p["seconds"] > 3.0 and p["status"] < 400]
    for p in slow:
        alerts.append(f"🟠 {p['url']} lenta ({p['seconds']}s)")
    return alerts


def seo_alerts(current: dict, previous: dict, drop: float = 0.4, min_base: int = 20) -> list[str]:
    """Alerta si los clics o impresiones orgánicos caen más de `drop` frente al periodo previo."""
    alerts = []
    for metric, label in (("clicks", "clics"), ("impressions", "impresiones")):
        base = previous.get(metric, 0)
        if base >= min_base and current.get(metric, 0) < base * (1 - drop):
            pct = round(100 * (1 - current[metric] / base))
            alerts.append(f"🔴 Caída de {label} orgánicos: {current[metric]} vs {base} ({pct}% menos)")
    return alerts


def conversion_alerts(ga: dict, min_sessions: int = 50) -> list[str]:
    """Tráfico sin ninguna conversión suele indicar etiqueta rota."""
    total = sum(ga["events"].values())
    if ga["sessions"] >= min_sessions and total == 0:
        return [f"🔴 {ga['sessions']} sesiones y 0 conversiones en 7 días: revisar etiquetas GA4/GTM"]
    return []


def render_report(audit: dict | None, seo: dict | None, ga: dict | None, opportunities: list[dict],
                  alerts: list[str], title: str = "UberTransfer") -> str:
    L = [f"# Informe {title}", ""]
    L.append("## Alertas" if alerts else "## Sin alertas")
    L += [f"- {a}" for a in alerts] or ["Todo dentro de los umbrales."]
    if audit:
        bad = [p for p in audit["pages"] if p["issues"]]
        L += ["", f"## Auditoría técnica ({len(audit['pages'])} páginas, {len(bad)} con observaciones)"]
        for p in bad:
            L.append(f"- {p['url']}: " + "; ".join(p["issues"]))
    if seo:
        L += ["", "## SEO (Search Console, 7 días)",
              f"- Clics: {seo['clicks']} · Impresiones: {seo['impressions']}"]
    if opportunities:
        L += ["", "## Oportunidades (posición 8–20 con demanda)"]
        for o in opportunities[:10]:
            L.append(f"- «{o['query']}» pos {o['position']} · {o['impressions']} impr. → {o['page']}")
    if ga:
        L += ["", "## Conversiones (GA4, 7 días)", f"- Sesiones: {ga['sessions']}"]
        L += [f"- {k}: {v}" for k, v in ga["events"].items()]
    return "\n".join(L) + "\n"
