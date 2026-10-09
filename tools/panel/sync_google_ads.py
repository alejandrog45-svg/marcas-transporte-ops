"""Descarga métricas de Google Ads para UberTransfer, solo lectura.

No contiene llamadas de mutación. Usa acceso Cloud administrado; si existe un
token de desarrollador heredado, lo envía por compatibilidad.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "google_ads_ubertransfer.json"
CUSTOMER_DEFAULT = "2035504421"
API_VERSION = "v25"


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta el secreto {name}")
    return value


def customer_id(value: str) -> str:
    value = value.replace("-", "")
    if not re.fullmatch(r"\d{10}", value):
        raise ValueError("GOOGLE_ADS_CUSTOMER_ID debe tener 10 dígitos")
    return value


def dates() -> tuple[str, str]:
    forced = os.environ.get("GOOGLE_ADS_DATE", "").strip()
    if forced:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", forced):
            raise ValueError("GOOGLE_ADS_DATE debe tener formato YYYY-MM-DD")
        return forced, forced
    today = dt.datetime.now(dt.timezone.utc).date()
    yesterday = today - dt.timedelta(days=1)
    value = yesterday.isoformat()
    return value, value


def query(date_from: str, date_to: str) -> str:
    return ("SELECT campaign.id, campaign.name, campaign.status, segments.date, "
            "metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.ctr, metrics.conversions FROM campaign "
            f"WHERE segments.date BETWEEN '{date_from}' AND '{date_to}' "
            "ORDER BY segments.date, campaign.id")


def report_queries(date_from: str, date_to: str) -> dict[str, str]:
    period = f"WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'"
    return {
        "hourly": ("SELECT segments.date, segments.hour, metrics.impressions, metrics.clicks, "
                   "metrics.cost_micros, metrics.conversions FROM campaign " + period + " ORDER BY segments.date, segments.hour"),
        "devices": ("SELECT segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros, "
                    "metrics.conversions FROM campaign " + period + " ORDER BY segments.device"),
        "adGroups": ("SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, segments.date, "
                     "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions "
                     "FROM ad_group " + period + " ORDER BY segments.date, campaign.id, ad_group.id"),
        "ads": ("SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group_ad.ad.id, "
                "ad_group_ad.ad.name, ad_group_ad.status, segments.date, metrics.impressions, "
                "metrics.clicks, metrics.cost_micros, metrics.conversions FROM ad_group_ad " + period +
                " ORDER BY segments.date, campaign.id, ad_group.id, ad_group_ad.ad.id"),
        "searchTerms": ("SELECT search_term_view.search_term, campaign.id, campaign.name, ad_group.id, "
                        "ad_group.name, segments.date, metrics.impressions, metrics.clicks, "
                        "metrics.cost_micros, metrics.conversions FROM search_term_view " + period + " ORDER BY segments.date, metrics.clicks DESC"),
        "regions": ("SELECT geographic_view.country_criterion_id, geographic_view.location_type, "
                    "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions "
                    "FROM geographic_view " + period + " ORDER BY geographic_view.country_criterion_id"),
    }


def post_json(url: str, headers: dict[str, str], body: dict) -> object:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Google Ads respondió HTTP {error.code}: {detail[:500]}") from error


def search_stream(customer: str, headers: dict[str, str], statement: str) -> list[dict]:
    payload = post_json(
        f"https://googleads.googleapis.com/{API_VERSION}/customers/{customer}/googleAds:searchStream",
        headers, {"query": statement})
    if not isinstance(payload, list):
        raise RuntimeError("Google Ads devolvió un SearchStream inválido")
    return [row for batch in payload for row in (batch.get("results") or [])]


def access_token() -> str:
    body = urllib.parse.urlencode({
        "client_id": required("GOOGLE_ADS_OAUTH_CLIENT_ID"),
        "client_secret": required("GOOGLE_ADS_OAUTH_CLIENT_SECRET"),
        "refresh_token": required("GOOGLE_ADS_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }).encode()
    request = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=body,
        headers={"content-type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"OAuth Google Ads respondió HTTP {error.code}") from error
    if not payload.get("access_token"):
        raise RuntimeError("OAuth Google Ads no devolvió access_token")
    return payload["access_token"]


def normalize(rows: list[dict], date_from: str, date_to: str) -> dict:
    campaigns = []
    for row in rows:
        metrics = row.get("metrics") or {}
        campaigns.append({
            "campaignId": str((row.get("campaign") or {}).get("id", "")),
            "name": (row.get("campaign") or {}).get("name", ""),
            "status": (row.get("campaign") or {}).get("status", "UNSPECIFIED"),
            "date": (row.get("segments") or {}).get("date"),
            "impressions": int(metrics.get("impressions", 0)),
            "clicks": int(metrics.get("clicks", 0)),
            "costMicros": int(metrics.get("costMicros", 0)),
            "costClp": round(int(metrics.get("costMicros", 0)) / 1_000_000),
            "ctr": float(metrics.get("ctr", 0)),
            "conversions": float(metrics.get("conversions", 0)),
        })
    totals = {
        key: sum(row[key] for row in campaigns)
        for key in ("impressions", "clicks", "costClp", "conversions")
    }
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    snapshot = {**totals, "dateFrom": date_from, "dateTo": date_to}
    history = [h for h in (previous.get("history") or []) if h.get("dateFrom") != date_from]
    history.append(snapshot)
    history = sorted(history, key=lambda h: h.get("dateFrom", ""))[-90:]
    current_names = sorted({row["name"] for row in campaigns if row["name"]})
    previous_names = sorted(previous.get("campaignNames") or [])
    alerts = []
    if previous_names and current_names != previous_names:
        alerts.append({"type": "campaign_name_changed", "previous": previous_names, "current": current_names})
    previous_ads = {str(x.get("adId")): x for x in (previous.get("adHistory") or []) if x.get("adId")}
    campaign_history = {str(x.get("campaignId")): x for x in (previous.get("campaignHistory") or []) if x.get("campaignId")}
    for row in campaigns:
        cid = row["campaignId"]
        old = campaign_history.get(cid, {})
        campaign_history[cid] = {
            "campaignId": cid, "name": row["name"], "status": row["status"],
            "firstSeen": old.get("firstSeen", date_from), "lastSeen": date_from,
        }
    return {
        "brand": "UberTransfer",
        "customerId": customer_id(os.environ.get("GOOGLE_ADS_CUSTOMER_ID", CUSTOMER_DEFAULT)),
        "campaignIds": sorted({row["campaignId"] for row in campaigns if row["campaignId"]}),
        "campaignNames": current_names,
        "campaignHistory": sorted(campaign_history.values(), key=lambda x: x["campaignId"]),
        "adHistory": list(previous_ads.values()),
        "alerts": alerts,
        "mode": "read_only",
        "status": "connected",
        "lastSync": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "Google Ads API",
        "metrics": snapshot,
        "history": history,
        "campaigns": campaigns,
    }


def compact_report(name: str, rows: list[dict]) -> list[dict]:
    compact = []
    for row in rows:
        m = row.get("metrics") or {}
        s = row.get("segments") or {}
        campaign = row.get("campaign") or {}
        group = row.get("adGroup") or row.get("ad_group") or {}
        st = row.get("searchTermView") or row.get("search_term_view") or {}
        item = {
            "date": s.get("date"),
            "impressions": int(m.get("impressions", 0)),
            "clicks": int(m.get("clicks", 0)),
            "costClp": round(int(m.get("costMicros", 0)) / 1_000_000),
            "conversions": float(m.get("conversions", 0)),
        }
        if name == "hourly":
            item["hour"] = int(s.get("hour", 0))
        elif name == "devices":
            item["device"] = s.get("device", "UNSPECIFIED")
        elif name == "adGroups":
            item.update({"campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", ""),
                         "adGroupId": str(group.get("id", "")), "adGroupName": group.get("name", "")})
        elif name == "ads":
            ad_group_ad = row.get("adGroupAd") or {}
            ad = ad_group_ad.get("ad") or {}
            item.update({"adId": str(ad.get("id", "")), "adName": ad.get("name", ""),
                         "adStatus": ad_group_ad.get("status", "UNSPECIFIED"),
                         "campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", ""),
                         "adGroupId": str(group.get("id", "")), "adGroupName": group.get("name", "")})
        elif name == "searchTerms":
            item.update({"term": st.get("searchTerm", ""), "campaignId": str(campaign.get("id", "")),
                         "campaignName": campaign.get("name", ""), "adGroupId": str(group.get("id", "")),
                         "adGroupName": group.get("name", "")})
        elif name == "regions":
            item.update({"countryCriterionId": str((row.get("geographicView") or {}).get("countryCriterionId", "")),
                         "locationType": (row.get("geographicView") or {}).get("locationType", "UNSPECIFIED")})
        compact.append(item)
    return compact
def main() -> None:
    date_from, date_to = dates()
    token = access_token()
    cid = customer_id(os.environ.get("GOOGLE_ADS_CUSTOMER_ID", CUSTOMER_DEFAULT))
    headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}
    if os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip():
        headers["developer-token"] = os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"].strip()
    if os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip():
        headers["login-customer-id"] = customer_id(os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"])
    rows = search_stream(cid, headers, query(date_from, date_to))
    result = normalize(rows, date_from, date_to)
    result["reports"] = {}
    for name, statement in report_queries(date_from, date_to).items():
        try:
            result["reports"][name] = compact_report(name, search_stream(cid, headers, statement))
        except RuntimeError as error:
            result["reports"][name] = {"error": str(error), "rows": []}
    ad_history = {str(x.get("adId")): x for x in (result.get("adHistory") or []) if x.get("adId")}
    for ad in result["reports"].get("ads", []):
        aid = ad.get("adId")
        if not aid:
            continue
        old = ad_history.get(aid, {})
        if old.get("name") and old["name"] != ad.get("adName"):
            result["alerts"].append({"type": "ad_name_changed", "adId": aid,
                                     "previous": old["name"], "current": ad.get("adName", "")})
        ad_history[aid] = {"adId": aid, "name": ad.get("adName", ""), "status": ad.get("adStatus", ""),
                           "campaignName": ad.get("campaignName", ""), "adGroupName": ad.get("adGroupName", ""),
                           "firstSeen": old.get("firstSeen", date_from), "lastSeen": date_from}
    result["adHistory"] = sorted(ad_history.values(), key=lambda x: x["adId"])
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "customerId": cid, "date": date_from, "rows": len(rows), "metrics": result["metrics"]}))


if __name__ == "__main__":
    main()
