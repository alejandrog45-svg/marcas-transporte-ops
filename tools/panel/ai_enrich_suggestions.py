"""Sugerencias redactadas por una IA (Gemini) a partir de datos reales de Google Ads.

Flujo: datos frescos (``google_ads_ubertransfer.json``) + historial acumulado
(``google_ads_history_ubertransfer.json``) -> hechos calculados en Python -> la IA
redacta propuestas citando esos hechos -> un validador descarta todo número que no
esté en los hechos citados -> ``data/ai_suggestions_latest.json``.

Reglas: la IA no calcula ni inventa cifras, no cambia campañas, pujas ni
presupuestos, y si falla (sin clave, red, formato) el paso termina sin error para
no interrumpir el workflow diario.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ADS_FILE = ROOT / "data" / "google_ads_ubertransfer.json"
HISTORY_FILE = ROOT / "data" / "google_ads_history_ubertransfer.json"
OUT_FILE = ROOT / "data" / "ai_suggestions_latest.json"
DEFAULT_MODEL = "gemini-3.6-flash"
FALLBACK_MODELS = ("gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-flash-latest")
MAX_SUGGESTIONS = 5
NUMBER = re.compile(r"\d[\d.,]*\d|\d")


def num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def detail_rows(name: str, data: dict[str, Any], history: dict[str, Any]) -> list[dict[str, Any]]:
    """Filas diarias de un informe: el historial acumulado y, si falta, el archivo fresco."""
    rows = (history.get("reports") or {}).get(name)
    if not isinstance(rows, list) or not rows:
        rows = (data.get("reports") or {}).get(name)
    return rows if isinstance(rows, list) else []


def aggregate(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "costClp": 0.0, "conversions": 0.0})
    for row in rows:
        label = str(row.get(key) if row.get(key) is not None else "").strip().lower()
        if not label:
            continue
        for field in ("clicks", "impressions", "costClp", "conversions"):
            acc[label][field] += num(row.get(field))
    out = [{key: label, **{k: round(v, 2) if k == "conversions" else int(round(v)) for k, v in vals.items()}} for label, vals in acc.items()]
    return sorted(out, key=lambda r: (-r["clicks"], -r["costClp"], r[key]))


def pct(value: Any) -> float | None:
    """Fracción de Google (0,62) -> porcentaje con un decimal (62,3). Sin dato -> None, nunca 0."""
    return None if value is None else round(num(value) * 100, 1)


def quality_rows(data: dict[str, Any], history: dict[str, Any], partial_day: str) -> list[dict[str, Any]]:
    """Cuota de impresiones y pérdidas por día. Las cuotas solo se informan con una campaña ese día."""
    # Por cada día manda la fuente más reciente: el historial trae los días viejos y los datos frescos
    # reemplazan al historial en los días que traen (el historial anterior no guardaba las cuotas).
    by_day: dict[str, list[dict[str, Any]]] = {}
    for source in ((history.get("reports") or {}).get("campaignQuality"), (data.get("reports") or {}).get("campaignQuality")):
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in source if isinstance(source, list) else []:
            if row.get("date"):
                grouped[str(row["date"])].append(row)
        by_day.update(grouped)
    out = []
    for day in sorted(by_day)[-14:]:
        rs = by_day[day]
        item: dict[str, Any] = {"fecha": day, "diaParcial": day == partial_day}
        for key, label in (("interactions", "interacciones"), ("invalidClicks", "clicsInvalidos"), ("phoneCalls", "llamadas")):
            vals = [num(r.get(key)) for r in rs if r.get(key) is not None]
            item[label] = int(sum(vals)) if vals else None
        if len(rs) == 1:
            r = rs[0]
            item.update({"cuotaImpresionesPct": pct(r.get("searchImpressionShare")),
                         "perdidaPorPresupuestoPct": pct(r.get("searchBudgetLostImpressionShare")),
                         "perdidaPorRankingPct": pct(r.get("searchRankLostImpressionShare")),
                         "cuotaPrimerasPosicionesPct": pct(r.get("searchTopImpressionShare"))})
        out.append({k: v for k, v in item.items() if v is not None})
    return out


def build_facts(data: dict[str, Any], history: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Hechos verificables calculados con reglas fijas. Cada uno lleva un id citable."""
    facts: dict[str, dict[str, Any]] = {}
    last_sync = str(data.get("lastSync") or "")
    partial_day = last_sync[:10]  # la descarga diaria corre por la mañana: ese día llega parcial
    daily = []
    for row in sorted(data.get("history") or [], key=lambda r: str(r.get("dateFrom", "")))[-14:]:
        clicks, impressions, cost = num(row.get("clicks")), num(row.get("impressions")), num(row.get("costClp"))
        daily.append({
            "fecha": row.get("dateFrom"), "impresiones": int(impressions), "clics": int(clicks), "costoClp": int(cost),
            "ctrPct": round(clicks / impressions * 100, 2) if impressions else None,
            "cpcClp": round(cost / clicks) if clicks else None,
            "conversiones": num(row.get("conversions")), "diaParcial": row.get("dateFrom") == partial_day,
        })
    facts["dias"] = {"descripcion": "Totales de la campaña por día (el día parcial aún no terminó)", "filas": daily}
    terms = aggregate(detail_rows("searchTerms", data, history), "term")
    facts["terminos_mas_clics"] = {"descripcion": "Términos de búsqueda con más clics, sumando todos los días del historial",
                                   "filas": [{"termino": r["term"], "clics": r["clicks"], "costoClp": r["costClp"], "conversiones": r["conversions"]} for r in terms[:10]]}
    costly = sorted([r for r in terms if r["clicks"] > 0 and r["conversions"] == 0], key=lambda r: -r["costClp"])[:5]
    facts["terminos_costosos_sin_conversion"] = {"descripcion": "Términos con más gasto y 0 conversiones registradas",
                                                 "filas": [{"termino": r["term"], "clics": r["clicks"], "costoClp": r["costClp"]} for r in costly]}
    hours = [r for r in aggregate(detail_rows("hourly", data, history), "hour") if r["clicks"] > 0]
    facts["horas"] = {"descripcion": "Clics y costo por hora del día, sumando el historial",
                      "filas": [{"hora": int(r["hour"]), "clics": r["clicks"], "costoClp": r["costClp"]} for r in sorted(hours, key=lambda r: int(r["hour"]))]}
    devices = aggregate(detail_rows("devices", data, history), "device")
    facts["dispositivos"] = {"descripcion": "Clics, impresiones y costo por dispositivo, sumando el historial",
                             "filas": [{"dispositivo": r["device"], "clics": r["clicks"], "impresiones": r["impressions"], "costoClp": r["costClp"]} for r in devices]}
    settings_rows = (data.get("reports") or {}).get("campaignSettings")
    settings = settings_rows[0] if isinstance(settings_rows, list) and settings_rows else {}
    facts["cuota_y_presupuesto"] = {
        "descripcion": ("Presupuesto diario y, por día, qué porcentaje de las impresiones posibles se obtuvo y cuánto se perdió "
                        "por presupuesto o por ranking. Un día parcial aún no terminó"),
        "presupuestoDiarioClp": settings.get("dailyBudgetClp"),
        "estrategiaDePuja": settings.get("biddingStrategy"),
        "filas": quality_rows(data, history, partial_day),
    }
    facts["cuota_y_presupuesto"] = {k: v for k, v in facts["cuota_y_presupuesto"].items() if v is not None}
    days = sorted({str(r.get("date")) for name in ("searchTerms", "hourly", "devices") for r in detail_rows(name, data, history) if r.get("date")})
    facts["cobertura"] = {"descripcion": "Cuántos días de historial detallado existen (pocos días = conclusiones débiles)",
                          "diasConDetalle": len(days), "desde": days[0] if days else None, "hasta": days[-1] if days else None,
                          "conversionesRegistradas": num((data.get("metrics") or {}).get("conversions"))}
    return facts


def build_prompt(facts: dict[str, dict[str, Any]], campaign: str) -> str:
    return (
        "Eres analista de Google Ads para UberTransfer (transfer y traslados en Chile). "
        "Recibes HECHOS ya calculados de la campaña \"" + campaign + "\". Redacta propuestas para que el dueño las revise a mano.\n"
        "REGLAS ESTRICTAS:\n"
        "- Usa solo los hechos entregados. No inventes ni calcules cifras nuevas; si citas un número, debe aparecer tal cual en un hecho que cites.\n"
        "- Cada propuesta debe citar al menos un id de hecho en \"refs\" (ids válidos: " + ", ".join(facts) + ").\n"
        "- Objetivo permanente: conseguir más clics de la campaña con datos reales. Prioriza lo que más clics podría aportar.\n"
        "- No ejecutes ni des por hecho cambios de presupuesto, pujas ni pausas. Si la pérdida por presupuesto o por ranking es alta, "
        "puedes proponer que el dueño EVALÚE cambiarlos, citando los porcentajes del hecho \"cuota_y_presupuesto\".\n"
        "- Si hay pocos días de historial (hecho \"cobertura\"), dilo y baja la confianza. El día con diaParcial=true no está completo.\n"
        "- Sin conversiones registradas no hables de rentabilidad ni de ventas: solo de tráfico.\n"
        "- Máximo " + str(MAX_SUGGESTIONS) + " propuestas, en español, claras y breves.\n"
        "Devuelve SOLO un arreglo JSON de objetos con las claves: title, action, reason, refs (arreglo de ids), confidence (\"Baja\" o \"Media\").\n\n"
        "HECHOS:\n" + json.dumps(facts, ensure_ascii=False)
    )


def call_gemini(prompt: str, api_key: str, model: str) -> tuple[list[dict[str, Any]], str]:
    """Pide las propuestas a Gemini. Si un modelo está saturado o no responde, prueba el siguiente."""
    import requests

    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}}
    last = "sin respuesta"
    for name in dict.fromkeys((model, *FALLBACK_MODELS)):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent"
        for attempt in range(2):
            response = requests.post(url, headers={"x-goog-api-key": api_key, "content-type": "application/json"}, json=body, timeout=60)
            if response.status_code in (429, 500, 502, 503) and attempt == 0:
                time.sleep(6)  # 503 = modelo saturado: un reintento corto y luego el siguiente modelo
                continue
            break
        if response.status_code != 200:
            last = f"{name}: HTTP {response.status_code}"
            continue
        try:
            parsed = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError, ValueError):
            last = f"{name}: respuesta sin formato JSON"
            continue
        if isinstance(parsed, list):
            return parsed, name
        last = f"{name}: no devolvió un arreglo"
    raise RuntimeError(f"Gemini no respondió ({last})")


def numbers_in(text: str) -> set[int]:
    """Números de un texto como enteros, ignorando separadores: «1.075» y «1075» valen igual."""
    return {int(re.sub(r"\D", "", token)) for token in NUMBER.findall(str(text))}


def allowed_numbers(fact: Any) -> set[int]:
    found: set[int] = set()
    if isinstance(fact, bool) or fact is None:
        return found
    if isinstance(fact, (int, float)):
        for pattern in (f"{fact}", f"{fact:.1f}", f"{fact:.2f}", f"{int(round(fact))}"):
            found |= numbers_in(pattern)
        return found
    if isinstance(fact, str):
        return numbers_in(fact)
    if isinstance(fact, list):
        for item in fact:
            found |= allowed_numbers(item)
    elif isinstance(fact, dict):
        for item in fact.values():
            found |= allowed_numbers(item)
    return found


def validate(suggestions: list[dict[str, Any]], facts: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Deja solo las propuestas cuyos números salen de los hechos que citan."""
    valid, rejected = [], []
    for item in suggestions[: MAX_SUGGESTIONS * 2]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        refs = [r for r in (item.get("refs") or []) if r in facts] if isinstance(item.get("refs"), list) else []
        if not title or not refs:
            rejected.append(f"{title or '(sin título)'}: sin hechos citados")
            continue
        allowed: set[int] = {0}
        for ref in refs:
            allowed |= allowed_numbers(facts[ref])
        extra = numbers_in(" ".join(str(item.get(k, "")) for k in ("title", "action", "reason"))) - allowed
        if extra:
            rejected.append(f"{title}: cifras que no están en los hechos citados {sorted(extra)}")
            continue
        confidence = item.get("confidence") if item.get("confidence") in ("Baja", "Media") else "Baja"
        valid.append({"title": title, "action": str(item.get("action", "")).strip(), "reason": str(item.get("reason", "")).strip(),
                      "confidence": confidence, "refs": refs})
        if len(valid) == MAX_SUGGESTIONS:
            break
    return valid, rejected


def enrich(data: dict[str, Any], history: dict[str, Any], api_key: str, model: str) -> dict[str, Any]:
    facts = build_facts(data, history)
    campaigns = data.get("campaignNames") or []
    raw, used_model = call_gemini(build_prompt(facts, ", ".join(campaigns) or "sin nombre"), api_key, model)
    valid, rejected = validate(raw, facts)
    return {
        "source": f"IA ({used_model}) sobre datos reales de Google Ads · solo lectura",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "adsLastSync": data.get("lastSync"),
        "accountId": str(data.get("customerId") or ""),
        "detailDays": facts["cobertura"]["diasConDetalle"],
        "suggestions": [{**s, "evidence": {ref: facts[ref] for ref in s["refs"]}} for s in valid],
        "rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT_FILE)
    parser.add_argument("--show-facts", action="store_true", help="imprime los hechos y termina, sin llamar a la IA")
    args = parser.parse_args()
    data, history = load_json(ADS_FILE), load_json(HISTORY_FILE)
    if not data:
        print("::warning::IA: no hay datos de Google Ads; se omite.")
        return 0
    if args.show_facts:
        print(json.dumps(build_facts(data, history), ensure_ascii=False, indent=2))
        return 0
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("::warning::IA: falta GEMINI_API_KEY; las sugerencias de IA se omiten.")
        return 0
    try:
        result = enrich(data, history, api_key, os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    except Exception as error:  # la IA es un extra: nunca debe romper el workflow diario
        print(f"::warning::IA: no se generaron sugerencias ({type(error).__name__}: {str(error)[:160]})")
        return 0
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "suggestions": len(result["suggestions"]), "rejected": len(result["rejected"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
