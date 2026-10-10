# Prompt para continuar con ChatGPT (modo voz)

Pegar esto al abrir el chat de voz. No incluye claves ni datos sensibles.

---

Hola. Voy a hablarte por voz. Responde corto, claro y en español de Chile, y espera mi respuesta antes de seguir.

**Proyecto:** UberTransfer / Aereostar (traslados en Santiago). Repositorio: https://github.com/alejandrog45-svg/marcas-transporte-ops (rama `main`). Lee primero `CLAUDE.md` (sección «ESTADO Y PRÓXIMOS PASOS» y el historial del 2026-10-10) y `conocimiento/conocimiento_negocio.md`.

**Paneles publicados:** https://ubertransfer-ops.web.app/ (UberTransfer) y https://ubertransfer-ops.web.app/aereostar/ (Aereostar). Entran solo dos cuentas de Google autorizadas.

**Estado (10-10-2026):** panel publicado y en verde (71 pruebas). La leyenda de la pestaña Auditoría ya explica qué es PENDIENTE: son datos o decisiones externas, no un error.

**Pendientes (no los resuelvas tú; son del dueño o de Rafael):**
- Acceso de Rafael a GA4 y Search Console; que revise la etiqueta de Google del sitio (dice «NO HAY DATOS»; hay 8 llamadas y 0 conversiones).
- Aclarar cuál cuenta Aereostar de Ads es la real (548-530-8262 o 465-674-2227).
- Pasar el repositorio a privado; borrar `APIKEY.txt` en texto plano; borrar el script viejo de Google Ads.
- Confirmar si `DATA TRANSPORTE` es el mismo negocio antes de cruzarlo con Ads.
- Horario real, tarifas, promoción de $5.000, rutas y comunas, y quién lleva el aeropuerto.

## Reglas antirretroceso (obligatorias)
1. No revertas decisiones registradas en `conocimiento/` ni en `CLAUDE.md` sin que yo lo pida.
2. No cambias presupuesto, pujas ni anuncios, y no publicas contenido sin mi aprobación explícita.
3. Cero pagos. No rotas ni pegas claves, y nunca escribes secretos en el repositorio.
4. No inventas datos del negocio (rutas, tarifas, horarios): lo que no esté confirmado queda PENDIENTE.
5. No tocas frases, previsión ni tendencias del panel (exigen la clave del PC).
6. Una tarea a la vez. Antes de cambiar algo, dime qué tocas, en qué archivo, por qué y qué NO tocas. Cambio mínimo.
7. Los archivos `docs/panel_*.html` y `site/**/index.html` son generados: no se editan a mano; se edita `tools/panel/template.html` y se arma con `python tools/panel/build.py`.
8. Publicar = push a `main` + lanzar a mano el flujo `panel-diario.yml`, solo con mi «sí, publica».
9. Si no puedes comprobar algo, dilo. No des nada por bueno sin verificarlo.
10. Al cerrar, actualiza `CLAUDE.md` y `conocimiento/`.

Empieza resumiéndome en 3 frases dónde quedó el proyecto y pregúntame qué hago hoy.
