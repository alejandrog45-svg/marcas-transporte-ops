# marcas-transporte-ops

Automatización de SEO, medición y monitoreo para **ubertransfer.cl**. Costo de infraestructura: ~US$0 (GitHub Actions + APIs gratuitas de Google).

Principio: el sistema **detecta y propone**. Gasto de Ads, publicación de contenido y cambios en el sitio los aprueba una persona.

## Qué hace hoy

| Job | Frecuencia | Necesita secretos | Salida |
|---|---|---|---|
| `audit` (workflow *Auditoría técnica semanal*) | Lunes | No | `reports/audit_latest.md`, histórico en `data/` |
| `seo` (workflow *SEO y conversiones diario*) | Diario | Sí (Google) | `reports/seo_latest.md`, oportunidades, alertas |

Si hay alertas se abre un **Issue** en este repo (GitHub te avisa por correo). Sin `GOOGLE_SA_JSON` el job `seo` se omite sin error.

## Puesta en marcha

1. Sigue `docs/setup_accesos.md` (tu parte manual, una sola vez).
2. Actions → *Auditoría técnica semanal* → *Run workflow* para la primera corrida.

## Uso local

```bash
pip install -r requirements-dev.txt
pytest -q
PYTHONPATH=src python -m marcas_transporte_ops audit
```

## Estructura

```
src/marcas_transporte_ops/   audit.py (sitio) · google_api.py (GSC/GA4) · analysis.py (reglas) · cli.py
tests/                  pruebas sin red
data/                   histórico de snapshots (lo escribe el bot)
reports/                último informe
docs/                   plan_ubertransfer_v2.html · setup_accesos.md
conocimiento/           datos verificados del negocio
```

Plan completo: `docs/plan_ubertransfer_v2.html`.
