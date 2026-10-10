# Traspaso nube → PC (sesión de nube del 2026-10-10, tarde)

Al abrir el PC, en la primera sesión de Claude Code local: «lee este archivo y ejecuta la sección *Al volver al PC*».

## Qué se comprobó desde la nube (hechos del 10-10)
- **Navegador del dueño (Chrome / Claude in Chrome):** NO disponible en la sesión de nube. Solo hay Chromium + Playwright sin sesiones (`/opt/pw-browsers`): sirve para probar los paneles sin login, no para entrar a Google Ads ni a cuentas. Nunca se escriben contraseñas ni 2FA.
- **Google Ads (Supermetrics, conector del dueño):** fuente `AW` en estado NOT_AUTHENTICATED. Falta que el dueño abra el enlace de acceso (lo entrega `data_source_discovery(ds_id="AW")`; es personal, no se guarda en el repo) y autorice la cuenta de datos `203-550-4421`. Igual con Search Console (`GW`) y GA4 (`GAWA`): sin conectar. Hasta entonces la nube NO lee Ads directamente.
- **GitHub:** la nube ve las 3 repos (`marcas-transporte-ops`, `Plataforma-anuncios`, `data-transporte`) con la cuenta `alejandrog45-svg`; rama de trabajo `ccr-8b4f70ce-5obz3r` en las tres.
- **Red:** salen peticiones a `ubertransfer-ops.firebaseapp.com` (200) y `ubertransfer.cl` (200). `googleads.googleapis.com` responde (404 en la raíz = alcanzable), pero no hay credenciales de Ads en la nube.

## Actualización (10-10, tras autorizar Supermetrics; solo lectura)
- **Google Ads (conectado):** cuentas visibles `926-538-5719` (propia, solo investigación), `203-550-4421` «ubertranfer» y `548-530-8262` «Aereostar». Datos reales 08 y 09-10 (CLP): UberTransfer 794 y 1.125 impresiones, 52 y 65 clics, costo 15.068 y 15.810, 0 conversiones; Aereostar 84 y 706 impresiones, 12 y 41 clics, costo 15.012 y 16.008, 0 conversiones. **Hallazgo:** la cuenta de Aereostar `548-530-8262` TIENE una campaña activa con gasto (los docs decían «sin campañas»): confirmar con Rafael quién la administra. La otra cuenta de Aereostar (`465-674-2227`) no aparece en esta conexión.
- **Search Console:** conectado, pero `sc-domain:ubertransfer.cl` da USER_PERMISSION_DENIED (propiedad sin verificar; sigue pendiente Rafael).
- **GA4:** solo ve la propiedad `cabrasgo` (otro proyecto, NO se leyó). La propiedad de ubertransfer (`G-26K0MDTFY1`) no es accesible hasta que Rafael dé acceso.

## Consistencia de datos (10-10, solo lectura; no se tocó código ni datos del panel)
- **UberTransfer: CONSISTENTE.** Supermetrics = `data/google_ads_ubertransfer.json` e historial en ambos días (08-10: 794 impr., 52 clics, $15.068; 09-10: 1.125, 65, $15.810; 0 conversiones).
- **Aereostar: MISMA cuenta y campaña del panel (verificado).** `548-530-8262` y la campaña `24331409273` («Campaign #1») son exactamente las de `data/google_ads_aereostar.json`; no es otra «Aerostar». El dueño la activó hace 1–2 días (confirmado por él). Google Ads la muestra ENABLED con datos desde el 08-10 (84 impr., 12 clics, $15.012) y 09-10 (706, 41, $16.008); 7 días: 790 impr., 53 clics, $31.020, 0 conversiones. El panel sigue diciendo «detenida, 0 gasto» solo porque su dato es la captura del 08-10 14:51 (anterior a la activación) y esa cuenta no se sincroniza: **dato desactualizado, no error de identidad**. No se modificó nada.
- **Antigüedad Aereostar (Google Ads por hora, hora de la cuenta):** primer dato 08-10 a las 21:00 (84 impr., 12 clics, $15.012 en esa sola hora); 09-10 de 08:00 a 20:00 con $9.006 a las 08:00 y el resto entre $0 y $1.050 por hora. Al 09-10 ~23:50 lleva ~1 día 3 h con datos; creada y pagada el 08-10, coherente con «hace ~2 días». Lo gastado (~$15–16 mil/día) coincide con el presupuesto diario de CLP 15.000.
- Propuesta (sin aplicar): sincronizar solo lectura la cuenta `548-530-8262` en `sync_google_ads.py` y mostrar la fecha de la lectura en el panel de Aereostar.

## Qué se puede hacer desde la nube sin el PC
1. **Publicar el panel:** push a `main` + flujo manual `panel-diario.yml` (usa Secrets de GitHub: `FIREBASE_SERVICE_ACCOUNT`, `GEMINI_API_KEY` y las de Google Ads de solo lectura que ya usa `tools/panel/sync_google_ads.py`). Una corrida diaria programada ya lee Google Ads, sugiere con IA y publica.
2. **Cambios de CSS/plantilla/texto** del panel (`python tools/panel/build.py`, solo Node). NO frases, previsión ni tendencias (exigen la clave cifrada del PC).
3. **Auditorías y lecturas del sitio** por los flujos de GitHub (`inspeccion-sitio.yml`, `auditoria-aereostar.yml`): nunca sondeos directos.
4. **Documentación, plan de medición, análisis de `data-transporte`** (datos agregados) y código de `Plataforma-anuncios` (pruebas con emulador local; sin Blaze ni producción).
5. **Leer Google Ads, GA4 y Search Console** solo cuando el dueño autorice los conectores de Supermetrics (enlace anterior): lectura; sin cambios de presupuesto, pujas ni anuncios.

## Qué NO se puede sin el PC
Firebase CLI local y `E:\config`, clave del panel (frases/previsión/tendencias), bóveda `_boveda`, memoria local de Claude, Chrome del dueño con sesiones, cualquier contraseña/2FA.

## Al volver al PC (ejecutar en este orden, una tarea a la vez)
1. Herramientas de **W:** (`W:\PROYECTOS CUENTA ALEJANDROG45\herramientas-portables\`), no las de E:. `gh` con `GH_CONFIG_DIR` de la cuenta `alejandrog45-svg`.
2. En cada carpeta local de las 3 repos (`marcas-transporte-ops`, `Plataforma-anuncios`, `data-transporte`):
   `git status` (no tocar archivos locales sin seguimiento) → `git fetch origin` → revisar PR en borrador de la rama `ccr-8b4f70ce-5obz3r` → si el dueño lo aprobó y se fusionó: `git checkout main && git pull origin main`.
3. `E:\ubertransfer-ops` es solo lectura (su git usa `oviedoem`): no ejecutar git ahí; la copia vigente es la de W: / `alejandrog45-svg`.
4. `python -m pytest -q` en `marcas-transporte-ops`; si cambiaron `data/panel_data*.enc.json`, no sobrescribirlos (`git checkout`).
5. Actualizar `conocimiento/` y `CLAUDE.md` (regla antirretroceso) con lo que haya pasado en el PC.
6. **Revocar lo dado a la nube:** autorización de Supermetrics (Google Ads/GA4/GSC) si se concedió, accesos GitHub extra de la sesión, y cualquier token pegado en el chat. Rotar solo si el dueño lo pide.

## Pendientes que siguen siendo del dueño / Rafael
Autorizar Supermetrics (si quiere lectura desde la nube), paso A (teléfono) y paso C (GTM/GA4, Rafael) de `docs/pasos_medicion_rafael_y_dueno.md`, repo a privado, `APIKEY.txt`, script de Ads, confirmar `DATA TRANSPORTE`, cuál cuenta Aereostar de Ads es la real.
