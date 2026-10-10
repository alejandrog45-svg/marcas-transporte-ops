# Prompt para sesión nueva de Claude Code (copiar y pegar completo)

No contiene claves ni contraseñas. Repositorio: https://github.com/alejandrog45-svg/marcas-transporte-ops (hoy PÚBLICO). Rama de trabajo: la que te asigne la sesión (la anterior fue `ccr-8b4f70ce-5obz3r`, PR #4 en borrador, con CI en verde).

---

Hola. Respóndeme siempre por audio (mp3 corto en español, voz sintética con gTTS, sin datos sensibles) y deja solo una línea de texto; los enlaces y listas largas sí van escritos. Regla permanente de toda la sesión.

## 0. Reglas obligatorias (no negociables)
- **Skills y reglas activas desde el primer mensaje:** PREVENCIÓN, SAFE CHANGE (declarar `TOCO / RAZÓN / NO TOCO` antes de cada cambio, cambio mínimo, probar antes y después), AHORRO DE TOKENS (leer solo lo necesario; no recapitular) y **REGLA ANTIRRETROCESO ESTRICTA**: no revertir ni romper nada hecho; no revertir decisiones de `conocimiento/` sin pedido expreso del dueño.
- Al iniciar y cerrar: leer y actualizar `CLAUDE.md` y `conocimiento/`.
- Una tarea a la vez. Cero pagos. Solo lectura en Google Ads: **no** cambiar presupuesto, pujas ni anuncios; no crear campañas.
- No publicar ni fusionar sin un «sí, publica» / «fusiona» explícito del dueño. Nunca contraseñas, 2FA ni claves: el login de Google lo hace el dueño.
- Proyecto independiente de la ferretería: no mezclar código, datos ni credenciales. Firebase siempre con `--account`; nunca `firebase login:use`.
- UberTransfer y Aereostar van **separados**: cada marca con su propio ID de Google Ads, archivos, historial, sugerencias y documento de Firestore.

## 1. Leer primero (en este orden, nada más)
1. `CLAUDE.md` (sección «ESTADO Y PRÓXIMOS PASOS» y el historial del 2026-10-10).
2. `conocimiento/conocimiento_negocio.md`.
3. `docs/ACCESOS_NUBE.md`, `docs/TRASPASO_NUBE_A_PC_2026-10-10.md` y `docs/plan_aereostar_paridad.md`.
Solo si hace falta: `docs/pasos_medicion_rafael_y_dueno.md`, `docs/plan_ubertransfer_v2.html`.

## 2. Qué está hecho (verificado el 10-10; nada publicado ni fusionado)
- PR #4 (borrador): sincronizador/sugerencias/IA parametrizados por marca (`ADS_BRAND`), pasos propios de Aereostar en `panel-diario.yml` (con `continue-on-error`, después de los de UberTransfer), flujo manual `ads-acceso-aereostar.yml` (solo lectura), regla de Firestore `panel/aiSuggestions_aereostar`, `.claude/settings.json` (solo lectura), huella de paneles (`tools/panel/huella_paneles.py` + `tests/golden/`) y **panel de Aereostar con las mismas 11 secciones que UberTransfer** (todo en `brand_aereostar()` de `build.py`; la plantilla NO se tocó).
- Comprobado: 78 pruebas OK, `check_seguridad` OK, el panel de UberTransfer sale **byte a byte igual** (huella = golden), CI en verde en todos los commits. El CI sí tiene `PANEL_DATA_KEY` (el log muestra «datos nuevos cifrados»), así que al fusionar el armado no se rompe.
- Aereostar: cuenta `548-530-8262`, campaña `24331409273` («Campaign #1», activa desde el 08-10). Su archivo `data/google_ads_aereostar.json` está sembrado con la lectura real del 08 y 09-10 (84/12/$15.012 y 706/41/$16.008, 0 conversiones, CLP); el flujo diario con la API lo reemplazará. UberTransfer coincide exacto con Google Ads.

## 3. Primera tarea: conectar el navegador (ya habilitado por el dueño)
El dueño habilitó el plugin **«Browser Use»** (tu Chrome o un navegador en la nube) en claude.ai → Customize → Plugins. En esta sesión:
1. Cárgalo con ToolSearch (palabras: `browser`, `chrome`, `browser-use`) y confirma con `ListPlugins` que figura habilitado.
2. Abre `https://ubertransfer-ops.firebaseapp.com/` en una pestaña NUEVA (y luego `/aereostar/`). Pide «Permitir» por sitio. Si el login de Google no está guardado, **detente y pídeselo al dueño**; no escribas contraseñas ni códigos.
3. Con sesión: revisa pestaña por pestaña ambos paneles (verificaciones, consola sin errores, 375/820/1366 px). Esperado en Aereostar tras publicar: 11 secciones, datos de la cuenta `548-530-8262`, ninguna cifra de UberTransfer.
4. Si ninguna herramienta de navegador aparece: dilo claro (no inventes hallazgos) y usa el Chromium con Playwright de `/opt/pw-browsers` para la prueba SIN login (el panel plano `docs/panel_*.html` armado con una clave de prueba en una copia aparte sirve para revisar secciones).
5. Supermetrics: pide al dueño abrir de nuevo los enlaces de acceso que entrega `data_source_discovery` (Google Ads `AW`; opcional GA4 `GAWA` y Search Console `GW`). La autorización no se guarda en el repo.

## 4. Pendientes, en este orden (una tarea a la vez; esperar el OK del dueño en lo marcado ★)
1. **Verificar el PR #4:** CI verde, revisar el diff completo contra `main`, confirmar huella de UberTransfer idéntica. ★ Fusionar solo con «fusiona».
2. Tras fusionar: lanzar `ads-acceso-aereostar.yml` y leer «ACCESO OK». Si falla por permisos, parar y pedir al dueño dar acceso a la cuenta `548-530-8262` (no rotar claves).
3. ★ **Publicar** con «sí, publica»: `panel-diario.yml` manual; luego comprobar en la URL publicada (con navegador y sesión) que UberTransfer sigue igual y Aereostar muestra sus 11 secciones y datos reales de su cuenta. Antes, **recomendar pasar el repo a privado** (el JSON de Aereostar quedaría en claro en un repo público).
4. **En el PC (no en la nube):** desplegar reglas de Firestore (`firebase deploy --only firestore:rules --project ubertransfer-ops --account alejandrog45@gmail.com`) para que las sugerencias de Aereostar se vean; `git pull` en las 3 carpetas locales (`marcas-transporte-ops`, `Plataforma-anuncios`, `data-transporte`) según `docs/TRASPASO_NUBE_A_PC_2026-10-10.md`; revocar accesos dados a la nube.
5. **Medición** (`docs/pasos_medicion_rafael_y_dueno.md`): paso A (teléfono: 7 de 8 llamadas perdidas) del dueño; paso C (GTM/GA4) de Rafael; pasos D y F solo con aprobación expresa.
6. **Aereostar:** confirmar con el dueño/Rafael teléfono, tarifas, horarios y presupuesto; la auditoría de aereostar.cl es manual a propósito (la del 10-10 ya está hecha); GSC sin permiso sobre `ubertransfer.cl` y GA4 sin acceso (Rafael).
7. Pendientes del dueño: repo privado, borrar `APIKEY.txt` y el script viejo de Ads, confirmar `DATA TRANSPORTE`, abogado por «Uber».

## 5. Al cerrar la sesión
Actualizar `CLAUDE.md` y `conocimiento/`, dejar PR en borrador con CI verde, y entregarme este mismo tipo de prompt actualizado en `.md`.
