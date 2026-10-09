"""Genera sugerencias de solo lectura después de sincronizar Google Ads.

Se ejecuta desde GitHub Actions con el JSON recién generado por
``sync_google_ads.py`` y actualiza ``panel/aiSuggestions`` en Firestore.
No crea campañas ni modifica Google Ads.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ADS_FILE = ROOT / "data" / "google_ads_ubertransfer.json"
PROJECT_ID = "ubertransfer-ops"
DOCUMENT = "panel/aiSuggestions"
DATASTORE_SCOPE = "https://www.googleapis.com/auth/datastore"


def firestore_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"nullValue": None}
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, list):
        return {"arrayValue": {"values": [firestore_value(x) for x in value]}}
    if isinstance(value, dict):
        return {"mapValue": {"fields": {str(k): firestore_value(v) for k, v in value.items()}}}
    return {"stringValue": str(value)}


def text(row: dict[str, Any] | None, *keys: str, default: str = "sin dato") -> str:
    for key in keys:
        value = (row or {}).get(key)
        if value not in (None, ""):
            return str(value)
    return default


def number(row: dict[str, Any] | None, key: str) -> float:
    try:
        return float((row or {}).get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def money(value: float) -> str:
    return str(round(value))


def evidence(
    detail: str,
    date: str,
    campaign: str,
    reason: str,
    confidence: str,
    confirm: str,
) -> dict[str, str]:
    return {
        "evidence": detail,
        "date": date,
        "campaign": campaign or "sin campaña identificada",
        "reason": reason,
        "confidence": confidence,
        "confirm": confirm,
    }


def rows(reports: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = reports.get(name, [])
    return value if isinstance(value, list) else []


def build_suggestions(data: dict[str, Any]) -> dict[str, Any]:
    reports = data.get("reports") or {}
    campaigns = data.get("campaigns") or []
    if not isinstance(campaigns, list):
        campaigns = []
    terms = rows(reports, "searchTerms")
    devices = rows(reports, "devices")
    hours = rows(reports, "hourly")
    regions = rows(reports, "regions")
    metrics = data.get("metrics") or {}
    updated_at = str(data.get("lastSync") or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"))
    active = [
        row for row in campaigns
        if text(row, "status", default="").upper() in {"ENABLED", "ACTIVE"}
    ]
    current_rows = active or campaigns
    current = max(current_rows, key=lambda r: number(r, "clicks"), default={})
    campaign = text(current, "name", "campaignName")
    campaign_status = text(current, "status", default="sin estado")
    history = data.get("history") or []
    if not isinstance(history, list):
        history = []
    history = sorted(history, key=lambda row: str(row.get("dateFrom", "")))
    latest = history[-1] if history else None
    previous = history[-2] if len(history) > 1 else None
    best_term = max(terms, key=lambda r: number(r, "clicks"), default=None)
    costly = sorted(
        [r for r in terms if number(r, "clicks") > 0 and number(r, "conversions") == 0 and number(r, "costClp") > 0],
        key=lambda r: number(r, "costClp"),
        reverse=True,
    )
    best_hour = max(hours, key=lambda r: number(r, "clicks"), default=None)
    best_region = max(regions, key=lambda r: number(r, "clicks"), default=None)

    suggestions = [
        {
            "title": "Crear campaña basada en la actual",
            "action": "Preparar un borrador manual usando la estructura observada.",
            "kind": "PROPUESTA",
            "data": evidence(
                f"Campaña actual: {campaign}; estado {campaign_status}; "
                f"{len(campaigns)} fila(s) de Google Ads y {len(history)} fecha(s) históricas.",
                updated_at,
                campaign,
                "Existe una campaña real para revisar antes de copiar.",
                "Media" if campaigns else "Baja",
                "Objetivo, presupuesto y conversiones.",
            ),
        },
        {
            "title": "Agregar palabras de alto rendimiento",
            "action": "Revisar manualmente el término con más clics." if best_term else "No agregar términos sin evidencia.",
            "kind": "TÉRMINO REAL" if best_term else "DATOS INSUFICIENTES",
            "data": evidence(
                (
                    f"«{text(best_term, 'term', 'searchTerm')}»: {number(best_term, 'clicks'):g} clics, "
                    f"costo {money(number(best_term, 'costClp'))}"
                ) if best_term else "No hay términos utilizables.",
                updated_at,
                text(best_term, "campaignName", default=campaign) if best_term else campaign,
                "La recomendación usa filas devueltas por Google Ads." if best_term else "No se inventan términos.",
                "Alta" if best_term and number(best_term, "conversions") > 0 else "Media" if best_term else "Baja",
                "Intención, concordancia y página de destino.",
            ),
        },
        {
            "title": "Revisar términos costosos sin conversiones",
            "action": "Revisar antes de pausar o convertir en negativa." if costly else "No hay alerta prioritaria.",
            "kind": "REVISAR" if costly else "SIN ALERTA",
            "data": evidence(
                (
                    f"«{text(costly[0], 'term', 'searchTerm')}»: costo {money(number(costly[0], 'costClp'))} "
                    "y 0 conversiones."
                ) if costly else "No hay filas con gasto y cero conversiones.",
                updated_at,
                text(costly[0], "campaignName", default=campaign) if costly else campaign,
                "Tiene gasto y clics, pero Google Ads no reportó conversiones." if costly else "No se fabrica una alerta.",
                "Media" if costly else "Baja",
                "Que el seguimiento de conversiones esté funcionando.",
            ),
        },
        {
            "title": "Comparar la campaña actual con el historial",
            "action": "Comparar manualmente el último período contra el anterior antes de cambiar de campaña." if latest and previous else "Esperar otra fecha sincronizada para comparar.",
            "kind": "HISTORIAL REAL" if latest and previous else "HISTORIAL INSUFICIENTE",
            "data": evidence(
                (
                    f"Último período {text(latest, 'dateFrom')}: {number(latest, 'clicks'):g} clics / "
                    f"{number(latest, 'impressions'):g} impresiones; anterior {text(previous, 'dateFrom')}: "
                    f"{number(previous, 'clicks'):g} clics / {number(previous, 'impressions'):g} impresiones."
                ) if latest and previous else
                f"Google Ads devolvió {len(history)} fecha(s) histórica(s); se requieren al menos 2.",
                str((latest or {}).get("dateFrom") or updated_at),
                campaign,
                "Permite evaluar una campaña nueva frente a la actividad acumulada sin confundir nombres con rendimiento." if latest and previous else "No se inventa una tendencia con una sola fecha.",
                "Media" if latest and previous else "Baja",
                "Confirmar fechas de inicio/detención y que ambos períodos sean comparables.",
            ),
        },
    ]
    # Estos datos quedan disponibles para futuras sugerencias, pero no se usan
    # para afirmar rentabilidad ni para hacer cambios automáticos.
    _ = devices, hours, best_hour, best_region, metrics
    return {
        "source": "GitHub Actions · Google Ads API · solo lectura",
        "accountId": str(data.get("customerId") or ""),
        "period": "LAST_30_DAYS",
        "updatedAt": updated_at,
        "suggestions": suggestions,
        "queryStatus": {name: isinstance(value, list) for name, value in reports.items()},
        "queryErrors": [str(value.get("error")) for value in reports.values() if isinstance(value, dict) and value.get("error")],
    }


def write_firestore(payload: dict[str, Any]) -> None:
    import requests
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
    if not raw:
        raise RuntimeError("Falta FIREBASE_SERVICE_ACCOUNT")
    info = json.loads(raw)
    credentials = service_account.Credentials.from_service_account_info(info, scopes=[DATASTORE_SCOPE])
    credentials.refresh(Request())
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{DOCUMENT}"
    fields = {key: firestore_value(value) for key, value in payload.items()}
    if payload.get("updatedAt"):
        fields["updatedAt"] = {"timestampValue": str(payload["updatedAt"])}
    response = requests.patch(
        url,
        headers={"Authorization": f"Bearer {credentials.token}"},
        json={"fields": fields},
        timeout=45,
    )
    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError(f"Firestore HTTP {response.status_code}: {response.text[:500]}")


def main() -> None:
    if not ADS_FILE.exists():
        raise RuntimeError(f"No existe {ADS_FILE}")
    data = json.loads(ADS_FILE.read_text(encoding="utf-8"))
    payload = build_suggestions(data)
    write_firestore(payload)
    print(json.dumps({"ok": True, "accountId": payload["accountId"], "suggestions": len(payload["suggestions"])}))


if __name__ == "__main__":
    main()
