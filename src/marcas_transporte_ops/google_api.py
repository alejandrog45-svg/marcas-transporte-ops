"""Search Console y GA4 con cuenta de servicio (solo lectura). Los imports de Google son perezosos."""
import datetime as dt
import json

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
]
KEY_EVENTS = ("click_whatsapp", "click_phone", "lead_submit", "booking_complete")


def _creds(sa_json: str):
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_info(json.loads(sa_json), scopes=SCOPES)


def _range(days: int, offset: int = 3):
    """Search Console publica con ~2-3 días de retraso."""
    end = dt.date.today() - dt.timedelta(days=offset)
    return (end - dt.timedelta(days=days - 1)).isoformat(), end.isoformat()


def gsc_query(sa_json: str, site: str, dimensions: list[str], days: int = 28, limit: int = 1000) -> list[dict]:
    from googleapiclient.discovery import build
    svc = build("searchconsole", "v1", credentials=_creds(sa_json), cache_discovery=False)
    start, end = _range(days)
    body = {"startDate": start, "endDate": end, "dimensions": dimensions, "rowLimit": limit}
    rows = svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
    return [{"keys": r["keys"], "clicks": r["clicks"], "impressions": r["impressions"],
             "ctr": r["ctr"], "position": r["position"]} for r in rows]


def gsc_totals(sa_json: str, site: str, days: int = 7, offset: int = 3) -> dict:
    from googleapiclient.discovery import build
    svc = build("searchconsole", "v1", credentials=_creds(sa_json), cache_discovery=False)
    start, end = _range(days, offset)
    rows = svc.searchanalytics().query(siteUrl=site, body={"startDate": start, "endDate": end}).execute().get("rows", [])
    r = rows[0] if rows else {"clicks": 0, "impressions": 0}
    return {"clicks": r["clicks"], "impressions": r["impressions"], "start": start, "end": end}


def ga4_events(sa_json: str, property_id: str, days: int = 7) -> dict:
    """Conteo de eventos clave y sesiones de los últimos `days` días."""
    from googleapiclient.discovery import build
    svc = build("analyticsdata", "v1beta", credentials=_creds(sa_json), cache_discovery=False)
    rng = [{"startDate": f"{days}daysAgo", "endDate": "yesterday"}]
    prop = f"properties/{property_id}"
    ev = svc.properties().runReport(property=prop, body={
        "dateRanges": rng, "dimensions": [{"name": "eventName"}], "metrics": [{"name": "eventCount"}]}).execute()
    ses = svc.properties().runReport(property=prop, body={
        "dateRanges": rng, "metrics": [{"name": "sessions"}]}).execute()
    return ga4_parse(ses, ev)


def ga4_parse(sessions_resp: dict, events_resp: dict) -> dict:
    """`sessions` sale de la métrica `sessions` de GA4 (no del conteo del evento session_start)."""
    counts = {r["dimensionValues"][0]["value"]: int(r["metricValues"][0]["value"])
              for r in events_resp.get("rows", [])}
    rows = sessions_resp.get("rows", [])
    sessions = int(rows[0]["metricValues"][0]["value"]) if rows else 0
    return {"sessions": sessions, "session_start_events": counts.get("session_start", 0),
            "events": {k: counts.get(k, 0) for k in KEY_EVENTS}}
