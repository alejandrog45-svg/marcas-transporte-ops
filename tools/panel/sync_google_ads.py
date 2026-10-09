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

METRIC_FIELDS = ("metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, "
                 "metrics.conversions")
# Keep this shared SELECT limited to metrics supported by every report resource
# used below. Advanced metrics are resource/segment-specific in Google Ads API
# v25 and can make the whole SearchStream fail with
# PROHIBITED_METRIC_IN_SELECT_OR_WHERE_CLAUSE. Optional fields remain supported
# by normalization when a compatible dedicated query supplies them.


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
    forced_from = os.environ.get("GOOGLE_ADS_DATE_FROM", "").strip()
    forced_to = os.environ.get("GOOGLE_ADS_DATE_TO", "").strip()
    if forced_from or forced_to:
        if not (re.fullmatch(r"\d{4}-\d{2}-\d{2}", forced_from) and
                re.fullmatch(r"\d{4}-\d{2}-\d{2}", forced_to)):
            raise ValueError("GOOGLE_ADS_DATE_FROM y GOOGLE_ADS_DATE_TO deben tener formato YYYY-MM-DD")
        if forced_from > forced_to:
            raise ValueError("GOOGLE_ADS_DATE_FROM no puede ser posterior a GOOGLE_ADS_DATE_TO")
        return forced_from, forced_to
    today = dt.datetime.now(dt.timezone.utc).date()
    yesterday = today - dt.timedelta(days=1)
    return yesterday.isoformat(), today.isoformat()


def query(date_from: str, date_to: str) -> str:
    return ("SELECT campaign.id, campaign.name, campaign.status, segments.date, " + METRIC_FIELDS + " FROM campaign "
            f"WHERE segments.date BETWEEN '{date_from}' AND '{date_to}' "
            "ORDER BY segments.date, campaign.id")


def report_queries(date_from: str, date_to: str) -> dict[str, str]:
    period = f"WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'"
    return {
        "hourly": ("SELECT segments.date, segments.hour, " + METRIC_FIELDS + " FROM campaign " + period + " ORDER BY segments.date, segments.hour"),
        "devices": ("SELECT segments.device, " + METRIC_FIELDS + " FROM campaign " + period + " ORDER BY segments.device"),
        "adGroups": ("SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, segments.date, "
                     + METRIC_FIELDS + " "
                     "FROM ad_group " + period + " ORDER BY segments.date, campaign.id, ad_group.id"),
        "ads": ("SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group_ad.ad.id, "
                "ad_group_ad.ad.name, ad_group_ad.status, segments.date, " + METRIC_FIELDS + " FROM ad_group_ad " + period +
                " ORDER BY segments.date, campaign.id, ad_group.id, ad_group_ad.ad.id"),
        "searchTerms": ("SELECT search_term_view.search_term, campaign.id, campaign.name, ad_group.id, "
                        "ad_group.name, segments.date, " + METRIC_FIELDS + " FROM search_term_view " + period + " ORDER BY segments.date, metrics.clicks DESC"),
        "regions": ("SELECT geographic_view.country_criterion_id, geographic_view.location_type, "
                    + METRIC_FIELDS + " "
                    "FROM geographic_view " + period + " ORDER BY geographic_view.country_criterion_id"),
        # Métricas de calidad solo a nivel campaña y por fecha (compatibles entre sí); si Google las
        # rechaza, el informe queda con error y el resto de la descarga sigue igual.
        "campaignQuality": ("SELECT campaign.id, campaign.name, segments.date, " + METRIC_FIELDS + ", "
                            "metrics.interactions, metrics.invalid_clicks, metrics.phone_calls, "
                            "metrics.search_impression_share, metrics.search_budget_lost_impression_share, "
                            "metrics.search_rank_lost_impression_share, metrics.search_top_impression_share, "
                            "metrics.absolute_top_impression_percentage, metrics.top_impression_percentage "
                            "FROM campaign " + period + " ORDER BY segments.date"),
        "dayOfWeek": ("SELECT segments.day_of_week, " + METRIC_FIELDS + " FROM campaign " + period +
                      " ORDER BY segments.day_of_week"),
        "networks": ("SELECT segments.ad_network_type, " + METRIC_FIELDS + " FROM campaign " + period +
                     " ORDER BY segments.ad_network_type"),
        "keywords": ("SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
                      "campaign.id, campaign.name, ad_group.id, ad_group.name, segments.date, " + METRIC_FIELDS + " "
                      "FROM keyword_view " + period + " ORDER BY segments.date, metrics.clicks DESC"),
        "conversionActions": ("SELECT conversion_action.id, conversion_action.name, conversion_action.category, "
                              "conversion_action.type, conversion_action.status, conversion_action.counting_type, "
                              "conversion_action.include_in_conversions_metric, "
                              "conversion_action.click_through_lookback_window_days, "
                              "conversion_action.view_through_lookback_window_days FROM conversion_action "
                              "ORDER BY conversion_action.name"),
        "campaignSettings": ("SELECT campaign.id, campaign.name, campaign.status, "
                             "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
                             "campaign.start_date_time, campaign.end_date_time, campaign_budget.amount_micros "
                             "FROM campaign ORDER BY campaign.id"),
        "locations": ("SELECT campaign.id, campaign.name, campaign_criterion.criterion_id, "
                      "campaign_criterion.type, campaign_criterion.negative, "
                      "campaign_criterion.location.geo_target_constant FROM campaign_criterion "
                      "WHERE campaign_criterion.type = LOCATION ORDER BY campaign.id, campaign_criterion.criterion_id"),
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
            "averageCpc": float(metrics.get("averageCpc", 0) or 0),
            "costPerConversion": float(metrics.get("costPerConversion", 0) or 0),
            "conversionsValue": float(metrics.get("conversionsValue", 0) or 0),
            "allConversions": float(metrics.get("allConversions", 0) or 0),
            "allConversionsValue": float(metrics.get("allConversionsValue", 0) or 0),
            "phoneCalls": float(metrics["phoneCalls"]) if metrics.get("phoneCalls") is not None else None,
            "messageChats": float(metrics["messageChats"]) if metrics.get("messageChats") is not None else None,
            "interactions": float(metrics["interactions"]) if metrics.get("interactions") is not None else None,
            "invalidClicks": int(metrics["invalidClicks"]) if metrics.get("invalidClicks") is not None else None,
            "searchImpressionShare": metrics.get("searchImpressionShare"),
            "searchBudgetLostImpressionShare": metrics.get("searchBudgetLostImpressionShare"),
            "searchRankLostImpressionShare": metrics.get("searchRankLostImpressionShare"),
            "searchTopImpressionShare": metrics.get("searchTopImpressionShare"),
            "absoluteTopImpressionPercentage": metrics.get("absoluteTopImpressionPercentage"),
            "topImpressionPercentage": metrics.get("topImpressionPercentage"),
        })
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    def make_snapshot(day: str, day_rows: list[dict]) -> dict:
        totals = {key: sum(row[key] for row in day_rows) for key in ("impressions", "clicks", "costClp", "conversions")}
        snapshot = {**totals, "dateFrom": day, "dateTo": day, "activityStatus": "con actividad"}
        for key in ("conversionsValue", "allConversions", "allConversionsValue", "phoneCalls", "messageChats", "interactions", "invalidClicks"):
            values = [row[key] for row in day_rows if row.get(key) is not None]
            snapshot[key] = sum(values) if values else None
        snapshot["averageCpc"] = round(snapshot["costClp"] / snapshot["clicks"], 2) if snapshot["clicks"] else None
        snapshot["costPerConversion"] = round(snapshot["costClp"] / snapshot["conversions"], 2) if snapshot["conversions"] else None
        for key in ("searchImpressionShare", "searchBudgetLostImpressionShare", "searchRankLostImpressionShare", "searchTopImpressionShare", "absoluteTopImpressionPercentage", "topImpressionPercentage"):
            values = [row[key] for row in day_rows if row.get(key) is not None]
            snapshot[key] = values[0] if len(values) == 1 else None
        return snapshot

    daily_rows: dict[str, list[dict]] = {}
    for row in campaigns:
        day = str(row.get("date") or "")
        if day:
            daily_rows.setdefault(day, []).append(row)
    daily_snapshots = [make_snapshot(day, daily_rows[day]) for day in sorted(daily_rows)]
    if daily_snapshots:
        snapshot = daily_snapshots[-1]
        returned_days = {h["dateFrom"] for h in daily_snapshots}
        history = [h for h in (previous.get("history") or []) if h.get("dateFrom") not in returned_days]
        history.extend(daily_snapshots)
    else:
        # Sin filas no significa que el rendimiento anterior sea cero: una
        # campaña detenida simplemente deja de generar actividad.
        snapshot = dict(previous.get("metrics") or {})
        snapshot["activityStatus"] = "sin actividad nueva"
        history = list(previous.get("history") or [])
    history = sorted(history, key=lambda h: h.get("dateFrom", ""))[-90:]
    current_names = sorted({row["name"] for row in campaigns if row["name"]}) or sorted(previous.get("campaignNames") or [])
    previous_names = sorted(previous.get("campaignNames") or [])
    alerts = []
    if previous_names and current_names != previous_names:
        alerts.append({"type": "campaign_name_changed", "previous": previous_names, "current": current_names})
    previous_ads = {str(x.get("adId")): x for x in (previous.get("adHistory") or []) if x.get("adId")}
    campaign_history = {str(x.get("campaignId")): x for x in (previous.get("campaignHistory") or []) if x.get("campaignId")}
    for row in campaigns:
        cid = row["campaignId"]
        old = campaign_history.get(cid, {})
        # La última fecha es el último día con filas, no el inicio de la consulta.
        seen = max(row.get("date") or date_from, old.get("lastSeen") or "")
        campaign_history[cid] = {
            "campaignId": cid, "name": row["name"], "status": row["status"],
            "firstSeen": old.get("firstSeen", date_from), "lastSeen": seen,
        }
    return {
        "brand": "UberTransfer",
        "customerId": customer_id(os.environ.get("GOOGLE_ADS_CUSTOMER_ID", CUSTOMER_DEFAULT)),
        "campaignIds": sorted({row["campaignId"] for row in campaigns if row["campaignId"]}) or sorted(previous.get("campaignIds") or []),
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
        "activityRows": len(campaigns),
        "activityStatus": "con actividad" if campaigns else "sin actividad nueva; se conserva el último dato real",
    }


# Consulta mínima de ajustes (sin fechas): respaldo si Google rechaza los campos de fecha.
CAMPAIGN_SETTINGS_BASIC = ("SELECT campaign.id, campaign.name, campaign.status, "
                           "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
                           "campaign_budget.amount_micros FROM campaign ORDER BY campaign.id")


def campaign_date(campaign: dict, key: str):
    """Fecha (AAAA-MM-DD) de inicio o término. Google usa 2037-12-30 para «sin fecha de término»."""
    raw = campaign.get(key + "Time") or campaign.get(key)
    day = str(raw)[:10] if raw else None
    return None if day == "2037-12-30" else day


def fetch_campaign_settings(cid: str, headers: dict, statement: str) -> list[dict]:
    try:
        return compact_report("campaignSettings", search_stream(cid, headers, statement))
    except RuntimeError as error:
        if "UNRECOGNIZED_FIELD" not in str(error):
            raise
        return compact_report("campaignSettings", search_stream(cid, headers, CAMPAIGN_SETTINGS_BASIC))


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
            "averageCpc": m.get("averageCpc"),
            "costPerConversion": m.get("costPerConversion"),
            "conversionsValue": m.get("conversionsValue"),
            "allConversions": m.get("allConversions"),
            "allConversionsValue": m.get("allConversionsValue"),
            "phoneCalls": m.get("phoneCalls"),
            "messageChats": m.get("messageChats"),
            "interactions": m.get("interactions"),
            "invalidClicks": m.get("invalidClicks"),
            "searchImpressionShare": m.get("searchImpressionShare"),
            "searchBudgetLostImpressionShare": m.get("searchBudgetLostImpressionShare"),
            "searchRankLostImpressionShare": m.get("searchRankLostImpressionShare"),
            "searchTopImpressionShare": m.get("searchTopImpressionShare"),
            "absoluteTopImpressionPercentage": m.get("absoluteTopImpressionPercentage"),
            "topImpressionPercentage": m.get("topImpressionPercentage"),
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
        elif name == "campaignQuality":
            item.update({"campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", "")})
        elif name == "dayOfWeek":
            item["dayOfWeek"] = s.get("dayOfWeek", "UNSPECIFIED")
        elif name == "networks":
            item["network"] = s.get("adNetworkType", "UNSPECIFIED")
        elif name == "keywords":
            criterion = row.get("adGroupCriterion") or {}
            keyword = criterion.get("keyword") or {}
            item.update({"keyword": keyword.get("text", ""), "matchType": keyword.get("matchType", "UNSPECIFIED"),
                         "campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", ""),
                         "adGroupId": str(group.get("id", "")), "adGroupName": group.get("name", "")})
        elif name == "conversionActions":
            action = row.get("conversionAction") or {}
            item = {"conversionActionId": str(action.get("id", "")), "name": action.get("name", ""),
                    "category": action.get("category", "UNSPECIFIED"), "type": action.get("type", "UNSPECIFIED"),
                    "status": action.get("status", "UNSPECIFIED"), "countingType": action.get("countingType", "UNSPECIFIED"),
                    "includeInConversionsMetric": bool(action.get("includeInConversionsMetric", False)),
                    "clickThroughLookbackDays": int(action.get("clickThroughLookbackWindowDays", 0) or 0),
                    "viewThroughLookbackDays": int(action.get("viewThroughLookbackWindowDays", 0) or 0)}
        elif name == "campaignSettings":
            campaign_budget = row.get("campaignBudget") or {}
            item = {"campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", ""),
                    "status": campaign.get("status", "UNSPECIFIED"), "channel": campaign.get("advertisingChannelType", "UNSPECIFIED"),
                    "biddingStrategy": campaign.get("biddingStrategyType", "UNSPECIFIED"),
                    "startDate": campaign_date(campaign, "startDate"), "endDate": campaign_date(campaign, "endDate"),
                    # Sin presupuesto en la respuesta es "sin dato", no 0.
                    "dailyBudgetClp": (round(int(campaign_budget["amountMicros"]) / 1_000_000)
                                       if campaign_budget.get("amountMicros") is not None else None)}
        elif name == "locations":
            criterion = row.get("campaignCriterion") or {}
            location = criterion.get("location") or {}
            item = {"campaignId": str(campaign.get("id", "")), "campaignName": campaign.get("name", ""),
                    "criterionId": str(criterion.get("criterionId", "")),
                    "geoTargetConstant": location.get("geoTargetConstant", ""),
                    "criterionType": criterion.get("type", "UNSPECIFIED"),
                    "negative": bool(criterion.get("negative", False))}
        compact.append(item)
    return compact


def geo_names(customer: str, headers: dict[str, str], resources: list[str]) -> dict[str, dict]:
    """Nombre de cada geoTargetConstant (p. ej. geoTargetConstants/2152 -> Chile)."""
    if not resources:
        return {}
    quoted = ",".join("'" + value.replace("'", "\\'") + "'" for value in resources)
    statement = ("SELECT geo_target_constant.resource_name, geo_target_constant.id, "
                 "geo_target_constant.name, geo_target_constant.canonical_name, "
                 "geo_target_constant.country_code, geo_target_constant.target_type, "
                 "geo_target_constant.status FROM geo_target_constant "
                 f"WHERE geo_target_constant.resource_name IN ({quoted})")
    mapping = {}
    for row in search_stream(customer, headers, statement):
        geo = row.get("geoTargetConstant") or {}
        mapping[str(geo.get("resourceName", ""))] = {
            "geoTargetId": str(geo.get("id", "")),
            "name": geo.get("name", ""),
            "canonicalName": geo.get("canonicalName", ""),
            "countryCode": geo.get("countryCode", ""),
            "targetType": geo.get("targetType", "UNSPECIFIED"),
            "geoStatus": geo.get("status", "UNSPECIFIED"),
        }
    return mapping


def enrich_geo_locations(customer: str, headers: dict[str, str], reports: dict) -> None:
    locations = reports.get("locations")
    if not isinstance(locations, list):
        return
    resources = sorted({str(x.get("geoTargetConstant")) for x in locations if x.get("geoTargetConstant")})
    mapping = geo_names(customer, headers, resources)
    for item in locations:
        item.update(mapping.get(str(item.get("geoTargetConstant", "")), {}))


def enrich_geo_regions(customer: str, headers: dict[str, str], reports: dict) -> None:
    """La vista geográfica entrega solo el ID del país: se le agrega su nombre."""
    regions = reports.get("regions")
    if not isinstance(regions, list):
        return
    resources = sorted({"geoTargetConstants/" + str(x["countryCriterionId"]) for x in regions if x.get("countryCriterionId")})
    mapping = geo_names(customer, headers, resources)
    for item in regions:
        item.update(mapping.get("geoTargetConstants/" + str(item.get("countryCriterionId", "")), {}))


QUALITY_SUMS = ("interactions", "invalidClicks", "phoneCalls")
QUALITY_SHARES = ("searchImpressionShare", "searchBudgetLostImpressionShare", "searchRankLostImpressionShare",
                  "searchTopImpressionShare", "absoluteTopImpressionPercentage", "topImpressionPercentage")


def apply_campaign_quality(result: dict) -> None:
    """Copia a metrics las métricas de calidad del MISMO día que metrics (no mezcla días).

    Los conteos se suman entre campañas; las cuotas (porcentajes) solo se copian si hay una única
    campaña ese día, porque un promedio de porcentajes no sería un dato real de Google.
    """
    rows = (result.get("reports") or {}).get("campaignQuality")
    metrics = result.get("metrics")
    if not isinstance(rows, list) or not rows or not isinstance(metrics, dict):
        return
    day = str(metrics.get("dateTo") or "")
    day_rows = [r for r in rows if str(r.get("date") or "") == day]
    if not day_rows:
        return
    for key in QUALITY_SUMS:
        values = [float(r[key]) for r in day_rows if r.get(key) is not None]
        if values:
            metrics[key] = sum(values)
    if len(day_rows) == 1:
        for key in QUALITY_SHARES:
            if day_rows[0].get(key) is not None:
                metrics[key] = float(day_rows[0][key])


HISTORY_NAME = "google_ads_history_ubertransfer.json"
HISTORY_KEEP_DAYS = 90
HISTORY_VALUES = ("impressions", "clicks", "costClp", "conversions")
# Métricas que no son dimensiones: en el historial solo se conservan HISTORY_VALUES.
HISTORY_DROP = frozenset((
    "averageCpc", "costPerConversion", "conversionsValue", "allConversions", "allConversionsValue",
    "phoneCalls", "messageChats", "interactions", "invalidClicks", "searchImpressionShare",
    "searchBudgetLostImpressionShare", "searchRankLostImpressionShare", "searchTopImpressionShare",
    "absoluteTopImpressionPercentage", "topImpressionPercentage", "ctr", "costMicros",
))


def update_report_history(reports: dict, previous_reports: dict | None, path: Path) -> dict:
    """Acumula por día los informes con fecha (términos, horas, dispositivos, etc.).

    Cada ejecución solo pide los últimos días: los días devueltos reemplazan a los
    guardados (el día de hoy llega parcial y luego completo) y los demás se
    conservan, hasta HISTORY_KEEP_DAYS. Un informe con error o sin filas no borra
    lo acumulado.
    """
    try:
        stored = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, ValueError):
        stored = {}
    acc = {k: list(v) for k, v in (stored.get("reports") or {}).items() if isinstance(v, list)}

    def dated(rows) -> bool:
        return isinstance(rows, list) and bool(rows) and isinstance(rows[0], dict) and "date" in rows[0]

    def compact(row: dict, name: str = "") -> dict:
        # campaignQuality es el único informe que conserva las cuotas de impresión y los conteos de calidad
        keep = HISTORY_VALUES + ((QUALITY_SUMS + QUALITY_SHARES) if name == "campaignQuality" else ())
        return {k: v for k, v in row.items() if k not in HISTORY_DROP or k in keep}

    if not acc:  # primera vez: se siembra con lo que ya tenía el archivo anterior
        for name, rows in (previous_reports or {}).items():
            if dated(rows):
                acc[name] = [compact(r, name) for r in rows]
    for name, rows in reports.items():
        if not dated(rows):
            continue
        fresh_days = {r.get("date") for r in rows}
        kept = [r for r in acc.get(name, []) if r.get("date") not in fresh_days]
        acc[name] = kept + [compact(r, name) for r in rows]
    days = sorted({r["date"] for rows in acc.values() for r in rows if r.get("date")})
    if len(days) > HISTORY_KEEP_DAYS:
        cutoff = days[-HISTORY_KEEP_DAYS]
        acc = {n: [r for r in rows if (r.get("date") or "") >= cutoff] for n, rows in acc.items()}
        days = days[-HISTORY_KEEP_DAYS:]
    for rows in acc.values():
        rows.sort(key=lambda r: r.get("date") or "")
    # Una fila por línea: los commits diarios quedan como diferencias pequeñas.
    head = {"brand": "UberTransfer", "keepDays": HISTORY_KEEP_DAYS, "days": days,
            "updatedAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")}
    body = ",\n".join(
        json.dumps(name, ensure_ascii=False) + ":[\n" +
        ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n]"
        for name, rows in sorted(acc.items())
    )
    text = json.dumps(head, ensure_ascii=False)[:-1] + ',"reports":{\n' + body + "\n}}\n"
    path.write_text(text, encoding="utf-8")
    return {"file": path.name, "days": len(days), "from": days[0] if days else None,
            "to": days[-1] if days else None}


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
            result["reports"][name] = (fetch_campaign_settings(cid, headers, statement) if name == "campaignSettings"
                                       else compact_report(name, search_stream(cid, headers, statement)))
        except RuntimeError as error:
            result["reports"][name] = {"error": str(error), "rows": []}
    try:
        enrich_geo_locations(cid, headers, result["reports"])
    except RuntimeError as error:
        result["geoLookupError"] = str(error)
    try:  # el nombre del país es un extra: si Google lo rechaza, el panel muestra el ID
        enrich_geo_regions(cid, headers, result["reports"])
    except RuntimeError as error:
        result["geoRegionLookupError"] = str(error)[:300]
    try:
        apply_campaign_quality(result)
    except (TypeError, ValueError) as error:  # un dato raro nunca debe romper la descarga
        result["qualityMetricsError"] = str(error)[:300]
    # El catálogo de campañas se consulta sin filtro de fecha: así una campaña
    # nueva aparece aunque todavía no haya generado impresiones y una campaña
    # detenida sigue visible sin fabricar métricas cero.
    settings = result["reports"].get("campaignSettings")
    if isinstance(settings, list):
        campaign_history = {str(x.get("campaignId")): x for x in result.get("campaignHistory", []) if x.get("campaignId")}
        names = set(result.get("campaignNames") or [])
        ids = set(result.get("campaignIds") or [])
        for item in settings:
            campaign_id = str(item.get("campaignId", ""))
            name = item.get("campaignName", "")
            if not campaign_id:
                continue
            old = campaign_history.get(campaign_id, {})
            campaign_history[campaign_id] = {
                "campaignId": campaign_id,
                "name": name,
                "status": item.get("status", old.get("status", "UNSPECIFIED")),
                "firstSeen": old.get("firstSeen", date_from),
                "lastSeen": old.get("lastSeen", date_from),
            }
            ids.add(campaign_id)
            if name:
                names.add(name)
        result["campaignHistory"] = sorted(campaign_history.values(), key=lambda x: x["campaignId"])
        result["campaignIds"] = sorted(ids)
        result["campaignNames"] = sorted(names)
    ad_history = {str(x.get("adId")): x for x in (result.get("adHistory") or []) if x.get("adId")}
    ads_report = result["reports"].get("ads", [])
    # A report-specific GAQL error is stored as {error, rows}; it must not be
    # iterated as if it were a list of ad rows or the whole sync would fail.
    for ad in ads_report if isinstance(ads_report, list) else []:
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
    try:
        # El archivo anterior sigue intacto aquí: sirve para sembrar el historial la primera vez.
        previous_reports = (json.loads(OUT.read_text(encoding="utf-8")).get("reports") if OUT.exists() else None)
        result["detailHistory"] = update_report_history(result["reports"], previous_reports, OUT.with_name(HISTORY_NAME))
    except Exception as error:  # el historial de detalle nunca debe romper la bajada de datos
        result["detailHistoryError"] = str(error)[:300]
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "customerId": cid, "date": date_from, "rows": len(rows), "metrics": result["metrics"]}))


if __name__ == "__main__":
    main()
