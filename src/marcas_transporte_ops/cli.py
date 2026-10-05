"""Uso: python -m marcas_transporte_ops {audit|seo}

- audit: revisa el sitio (no necesita secretos).
- seo:   extrae Search Console + GA4 (necesita GOOGLE_SA_JSON; sin él, sale sin error).

Escribe reports/audit_latest.md o reports/seo_latest.md y, si hay alertas, reports/alerts.md (el workflow abre un Issue).
Los snapshots se guardan en data/ como histórico.
"""
import json
import pathlib
import sys
import time

from . import analysis, audit, config, google_api

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA, REPORTS = ROOT / "data", ROOT / "reports"


def _save(name: str, obj: dict) -> None:
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _save_status(status: dict) -> None:
    """Estado de la extracción SEO; solo se reescribe si cambia (evita commits diarios vacíos)."""
    f = DATA / "seo_status.json"
    if f.exists() and json.loads(f.read_text(encoding="utf-8")) == status:
        return
    _save("seo_status.json", status)


def _write(alerts: list[str], report: str, name: str, alerts_name: str = "alerts.md") -> None:
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / name).write_text(report, encoding="utf-8")
    alerts_file = REPORTS / alerts_name
    if alerts:
        alerts_file.write_text("\n".join(f"- {a}" for a in alerts) + "\n", encoding="utf-8")
    elif alerts_file.exists():
        alerts_file.unlink()


def cmd_audit(cfg) -> int:
    # Con AUDIT_TAG (p. ej. "aereostar") los archivos llevan la etiqueta y NO se pisan los de UberTransfer ni su alerts.md.
    tag = cfg.audit_tag
    sfx = f"_{tag}" if tag else ""
    title = tag.capitalize() if tag else "UberTransfer"
    alerts_name = f"alerts{sfx}.md"
    try:
        res = audit.run(cfg.site_url, delay=cfg.audit_delay, max_urls=cfg.audit_max_urls)
    except audit.AuditError as e:
        # No se pisa data/audit_latest.json: se conserva la última auditoría buena.
        _write([f"🔴 Auditoría NO ejecutada: {e}"], f"# Informe {title}\n\nAuditoría no ejecutada: {e}\n", f"audit{sfx}_latest.md", alerts_name)
        print(f"::error title=Auditoría no ejecutada::{e}")
        return 1
    _save(f"audit{sfx}_latest.json", res)
    alerts = analysis.audit_alerts(res)
    _write(alerts, analysis.render_report(res, None, None, [], alerts, title=title), f"audit{sfx}_latest.md", alerts_name)
    print(f"{len(res['pages'])} páginas auditadas, {len(alerts)} alertas")
    return 0


def cmd_seo(cfg) -> int:
    missing = [n for n, v in (("GOOGLE_SA_JSON", cfg.has_google), ("GSC_SITE", cfg.gsc_site),
                              ("GA4_PROPERTY_ID", cfg.ga4_property_id)) if not v]
    if not cfg.has_google or not cfg.gsc_site:
        _save_status({"state": "sin_conectar", "missing": missing})
        print("::warning title=SEO diario NO ejecutado::faltan " + ", ".join(missing) + " (ver docs/setup_accesos.md). No hay datos reales de Search Console/GA4.")
        return 0
    cur = google_api.gsc_totals(cfg.google_sa_json, cfg.gsc_site, days=7, offset=3)
    prev = google_api.gsc_totals(cfg.google_sa_json, cfg.gsc_site, days=7, offset=10)
    rows = google_api.gsc_query(cfg.google_sa_json, cfg.gsc_site, ["query", "page"], days=28)
    opps = analysis.find_opportunities(rows)
    ga = google_api.ga4_events(cfg.google_sa_json, cfg.ga4_property_id) if cfg.ga4_property_id else None
    alerts = analysis.seo_alerts(cur, prev) + (analysis.conversion_alerts(ga) if ga else [])
    stamp = time.strftime("%Y-%m-%d")
    _save(f"seo_{stamp}.json", {"totals": cur, "previous": prev, "opportunities": opps, "ga4": ga})
    _write(alerts, analysis.render_report(None, cur, ga, opps, alerts), "seo_latest.md")
    _save_status({"state": "ok", "missing": missing, "lastRun": stamp})
    print(f"SEO ok: {cur['clicks']} clics, {len(opps)} oportunidades, {len(alerts)} alertas")
    return 0


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    cmds = {"audit": cmd_audit, "seo": cmd_seo}
    if not argv or argv[0] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[0]](config.load())


if __name__ == "__main__":
    raise SystemExit(main())
