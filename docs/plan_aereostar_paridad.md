# Plan: panel de Aereostar con las mismas funciones que UberTransfer (datos 100 % propios)

Estado: PLAN (10-10-2026, sesión de nube). Nada de esto está aplicado. Regla antirretroceso: UberTransfer no cambia; cada paso se prueba con el panel de UberTransfer idéntico antes/después. Una tarea a la vez, rama aparte, sin publicar hasta «sí, publica» del dueño. Solo lectura de Google Ads; sin tocar presupuesto, pujas ni anuncios.

## Diagnóstico (verificado en el código)
- Panel UberTransfer = modo «Ads en vivo» (`plannerActive:false`): lee `data/google_ads_ubertransfer.json` + historial 90 días + sugerencias (reglas e IA) + auditoría diaria + Auditoría/Mejoras/Guía.
- Panel Aereostar = modo «solo información» (`plannerActive:true`): frases del Planificador como referencia, `data/google_ads_aereostar.json` sin sincronizar (captura del 08-10), 8 menús, sin Auditoría/Mejoras/Guía de Ads.
- Lo que hoy está fijo a UberTransfer y hay que parametrizar: `sync_google_ads.py` (`OUT`, `HISTORY_NAME`, cliente por defecto 2035504421), `sync_suggestions_firestore.py` (documento `panel/aiSuggestions`), `ai_enrich_suggestions.py` (`data/ai_suggestions_latest.json`), `panel-diario.yml` (un solo bloque de Ads), `build.py` (Aereostar usa `plannerActive=True` y lee el JSON sin historial/IA) y la plantilla (secciones, PWA y verificaciones se activan con `plannerActive===false`).
- Cuenta Aereostar de Ads: `548-530-8262`, campaña `24331409273` (misma del panel; activada por el dueño el 08-10).

## Principio de aislamiento
Cada marca tiene su propio ID de cliente, archivo de datos, historial, sugerencias, documento de Firestore y bloque cifrado. Ningún archivo ni variable se comparte, salvo el código. Un fallo de Aereostar nunca puede detener a UberTransfer (pasos propios con `continue-on-error` y el de UberTransfer queda primero y sin cambios).

## Pasos (cada uno: cambio mínimo, pruebas, commit pequeño; no se pasa al siguiente sin verde)
0. **Red de seguridad (solo pruebas).** Prueba que arma UberTransfer y guarda una huella del panel generado (sin `builtAt`); tras cada paso debe ser idéntica. TOCO: `tests/`. NO TOCO: nada más.
   - **HECHO (10-10, nube):** `tools/panel/huella_paneles.py` + `tests/test_huella_paneles.py` + `tests/golden/huella_paneles.json`. El armado es determinista (dos armados seguidos = misma huella, sin la hora). Uso: `python tools/panel/build.py && python tools/panel/huella_paneles.py`; la prueba se omite si `docs/` no está armado. En los pasos 5–6 la plantilla cambia de texto: allí la huella de UberTransfer solo se actualiza (`--actualizar`) tras comprobar en navegador que su comportamiento es idéntico, y se documenta.
1. **Acceso de lectura a 548-530-8262 (verificación, sin código).** Confirmar que las credenciales OAuth actuales (Secrets existentes) pueden leer esa cuenta; si Google exige `login-customer-id`, anotar cuál. Prueba: ejecución manual de solo lectura. Si falla: parar y pedir al dueño dar acceso (no se rotan claves).
2. **Parametrizar `sync_google_ads.py`.** Variables `ADS_BRAND`/`GOOGLE_ADS_CUSTOMER_ID` con los mismos valores por defecto de hoy (UberTransfer sin cambio) y nombres de salida por marca (`google_ads_aereostar.json`, `google_ads_history_aereostar.json`). Prueba: UberTransfer produce el mismo JSON; Aereostar produce el suyo.
3. **Paso propio de Aereostar en `panel-diario.yml`** (después del de UberTransfer, `continue-on-error`). Primero ejecución manual y revisar que los datos coincidan con Google Ads (hoy: 08-10 84/12/$15.012; 09-10 706/41/$16.008).
4. **Sugerencias propias.** `sync_suggestions_firestore.py` → documento `panel/aiSuggestions_aereostar`; `ai_enrich_suggestions.py` → `data/ai_suggestions_aereostar.json`; las reglas de Firestore deben permitir leer ese documento a los mismos 2 correos (revisar `firestore.rules`; el despliegue de reglas necesita aprobación). La IA solo ve datos de su marca.
5. **`build.py`: Aereostar en modo Ads en vivo** con un indicador propio (`liveAds`), sin reutilizar `plannerActive` de UberTransfer. Lee su historial, IA y auditoría (`audit_aereostar_latest.json`). Se guarda cifrado en `panel_data_aereostar.enc.json` (necesita armar en el PC por la clave; desde la nube se reutiliza el cifrado → este paso se prepara en la nube y se cierra en el PC).
6. **Plantilla: activar en Aereostar las mismas secciones** (Resumen, Campañas y anuncios, Rendimiento, Segmentos, Sugerencias, Historial, Palabras clave, Datos y verificación, Auditoría, Mejoras del sitio, Guía) con la condición `liveAds||plannerActive===false`; textos propios de Aereostar (teléfono/tarifas PENDIENTE hasta que Rafael confirme). Sin copiar nada de UberTransfer a los datos. Prueba: huella de UberTransfer idéntica; pestañas de Aereostar a 375/820/1366 px.
7. **Verificaciones y Auditoría propias.** Las comprobaciones de coherencia comparan Aereostar con SU historial; la Auditoría usa el sitio aereostar.cl (flujo `auditoria-aereostar.yml`, manual a propósito) y sus pendientes (`AE_BIZ`).
8. **Pruebas finales:** `python -m pytest -q`, `python tools/check_seguridad.py`, armado, Playwright sin login (carga y 0 errores en consola) y huella de UberTransfer idéntica.
9. **Publicar** solo con «sí, publica»: push a `main` + `panel-diario.yml`; verificar en la URL publicada con sesión del dueño (19/19 en ambos).

## Riesgos y decisiones del dueño
- **Repo público:** `data/google_ads_aereostar.json` quedaría en claro (como ya ocurre con UberTransfer). Recomendado pasar el repo a privado ANTES del paso 3, o excluir esos JSON del repo y guardarlos solo cifrados.
- **Rama y publicación:** una rama `aereostar-paridad` desde `main`, PR en borrador por paso; nada se publica sin aprobación.
- **Qué falta del PC:** armar con la clave (paso 5) y reglas de Firestore (paso 4) si el dueño aprueba desplegarlas.
- Pendientes ajenos al plan: teléfono, tarifas y horarios de Aereostar (Rafael), PWA de Aereostar (hoy solo UberTransfer; no se cambia).
