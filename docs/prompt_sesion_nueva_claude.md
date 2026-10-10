# Prompt para abrir una sesión NUEVA de Claude Code (copiar y pegar)

Pegar completo al iniciar la sesión nueva, en el repositorio indicado. No contiene claves ni contraseñas.

---

Hola. Respóndeme siempre por audio (mp3 corto en español, voz sintética con gTTS, sin datos sensibles) y deja solo una línea de texto. Esta regla es permanente en toda la sesión.

## 1. Repositorio y dónde trabajar
- Repositorio: https://github.com/alejandrog45-svg/marcas-transporte-ops (rama `main`; hoy es PÚBLICO).
- Proyecto UberTransfer / Aereostar (traslados en Santiago). Independiente de la ferretería: no mezclar código, datos ni credenciales.
- Paneles publicados (solo entran `alejandrog45@gmail.com` y `alimentosaltoque76@gmail.com`):
  - UberTransfer: https://ubertransfer-ops.web.app/ (redirige a https://ubertransfer-ops.firebaseapp.com/)
  - Aereostar: https://ubertransfer-ops.web.app/aereostar/
- Sitio real de Rafael: https://ubertransfer.cl (no sondear rutas de escáner ni hacer ráfagas).
- Lee primero, en este orden: `CLAUDE.md` (sección «ESTADO Y PRÓXIMOS PASOS» y el historial del 2026-10-10), `conocimiento/conocimiento_negocio.md`, `docs/pasos_medicion_rafael_y_dueno.md`. Lee `docs/plan_ubertransfer_v2.html` solo si hace falta (ahorra tokens).
- Trabaja en la rama de desarrollo que te asigne la sesión; abre PR en borrador y suscríbete a su actividad. No fusiones sin que yo lo diga.

## 2. Primera tarea: probar las conexiones de Chrome / navegador (desde la nube)
Yo ya activé en claude.ai/customize los plugins «Browser Use» y «Productivity» y el conector «Chrome Extension» (etiqueta Comunidad, no oficial). Verifica con evidencia, sin dar nada por hecho:
1. `ListPlugins`, `ListConnectors` (palabras: chrome, browser) y `ToolSearch` (browser, chrome, navigate, screenshot). Anota qué herramientas de navegador existen de verdad en esta sesión (por ejemplo `mcp__claude-in-chrome__*`, `enable__mcp__claude-in-chrome`, `mcp__Claude_Browser__*`, Browser Use).
2. Si existe una herramienta para habilitar Chrome, llámala. Carga las herramientas en UNA sola llamada de `ToolSearch`.
3. Con Chrome: `tabs_context_mcp` primero; abre una pestaña NUEVA (no reutilices las mías) en `https://ubertransfer-ops.firebaseapp.com/`. Si pide permiso por sitio, dímelo y espera a que yo pulse «Permitir».
4. Si Chrome no responde (mi PC puede estar apagado), prueba el navegador en la nube de Browser Use.
5. Si ninguna herramienta funciona, usa el Chromium de la nube con Playwright (`/opt/pw-browsers`, Playwright global de Node) para una prueba SIN login: ambos paneles a 375 px, sin errores de consola ni desbordes horizontales. Esa prueba ya pasó el 10-10.
6. Si fallan 2 o 3 intentos, para y explícame qué intentaste. No reintentes lo mismo.
7. Si el login con Google no está guardado, NO escribas contraseñas, códigos ni verificación en dos pasos: lo hago yo. Dentro del panel (con sesión), revisa pestaña por pestaña: Verificaciones 19/19 en «Datos y verificación», Auditoría 8/8, consola sin errores, y que la hora del encabezado se vea completa en celular.
8. Cuida el conector de Chrome «Comunidad»: dime qué permisos pide («puede enviar datos a otros servicios») antes de usarlo con datos del panel.

## 3. Estado al 2026-10-10
- Panel publicado y en verde (71 pruebas). Última publicación: `panel-diario.yml` ejecución 35, 13/13 pasos OK.
- Leyenda de Auditoría: PENDIENTE = dato o decisión externa (lista `BIZ`), en ámbar. Sello de hora del encabezado en varias líneas en celular; barras del menú móvil ocultas.
- Automatización: el cron dice 11:45 UTC, pero GitHub lo ejecuta ~6 h tarde (≈14:30–15:00 hora de Chile). Flujo: auditoría → Google Ads (solo lectura, historial 90 días) → sugerencias por reglas → IA Gemini (Secret `GEMINI_API_KEY`) → armar → guardar → publicar. La IA es Gemini, no Gmail.
- PR #1 (docs: hallazgos de accesos GA4/Search Console y etiqueta de Google sin datos) sigue en borrador.

## 4. Pendientes (NO los resuelvas tú; son del dueño o de Rafael)
- Rafael: acceso a GA4 y Search Console; revisar la etiqueta de Google del sitio (dice «NO HAY DATOS»; hay 8 llamadas y 0 conversiones; 7 de 8 llamadas figuran perdidas).
- Dueño: aclarar cuál cuenta Aereostar de Ads es la real (548-530-8262 o 465-674-2227); pasar el repositorio a privado; borrar `varios txt\APIKEY.txt`; borrar el script viejo de Google Ads «UberTransfer - Sugerencias Google Ads» (cuenta 203-550-4421); confirmar si `DATA TRANSPORTE` es el mismo negocio antes de cruzarlo con Ads.
- Negocio: horario real (el sitio dice 24/7, el schema 09:00–17:00), tarifas de los tramos 18:00–19:30 y 06:00–07:30, promoción de $5.000, rutas y comunas, quién lleva el aeropuerto, teléfono/tarifas/horarios de Aereostar, nombre «Uber» con abogado de propiedad industrial.
- Medición: paso A (revisar el teléfono de los anuncios) y paso C (GTM/GA4 para Rafael) están en `docs/pasos_medicion_rafael_y_dueno.md`. Los pasos D (libro de contactos) y F (subir conversiones) requieren mi aprobación expresa.

## 5. Reglas antirretroceso (obligatorias)
1. Activa en cada sesión: Prevención, Safe Change (cambio mínimo, una tarea a la vez), Ahorro de tokens y Regla antirretroceso.
2. No reviertas decisiones registradas en `conocimiento/` ni en `CLAUDE.md` sin que yo lo pida.
3. Antes de tocar código declara `TOCO / ARCHIVO / RAZÓN / NO TOCO`, haz el cambio mínimo y corre `python3 -m pytest -q` (hoy: 71 pruebas).
4. No cambies presupuesto, pujas ni anuncios, y no publiques contenido sin mi aprobación explícita. Cero pagos. No rotes ni pegues claves. Nunca secretos en el repositorio.
5. No inventes datos del negocio (rutas, tarifas, horarios, cifras): lo no confirmado queda PENDIENTE. Si no puedes comprobar algo, dilo.
6. No toques frases, previsión ni tendencias del panel (exigen la clave del PC; los `.enc.json` se reutilizan).
7. Los archivos `docs/panel_*.html` y `site/**/index.html` son GENERADOS: se edita `tools/panel/template.html` (y `extra.css`) y se arma con `python tools/panel/build.py`; el CI no tiene Pillow.
8. Publicar = push a `main` + lanzar a mano `panel-diario.yml`, solo con mi «sí, publica». Después comprueba que nada se rompió.
9. Firebase: siempre con `--account`; nunca `firebase login:use`. En la nube no hay Firebase CLI ni la clave del panel.
10. Al cerrar la sesión actualiza `CLAUDE.md` (historial) y `conocimiento/`, y dime qué quedó pendiente.

Empieza con la sección 2 (probar las conexiones de Chrome), reporta por audio qué herramientas encontraste y qué funcionó, y pregúntame qué hago después.
