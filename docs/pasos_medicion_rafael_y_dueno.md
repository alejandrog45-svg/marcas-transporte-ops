# Pasos de medición listos para ejecutar (paso A y paso C)

Complementa `docs/medicion_conversiones_plan.md`. No cambia presupuesto, pujas ni anuncios. Sin pagos.
Estado real del 09-10-2026: 8 llamadas desde anuncios, 7 perdidas (`MISSED`), 1 contestada de 18 s, 0 conversiones.

## Paso A · Dueño: revisar el teléfono que reciben los anuncios (15 min)
- [ ] Confirmar a qué número llama el anuncio y que ese teléfono lo atiende una persona (no es un número fuera de servicio ni sin señal).
- [ ] Confirmar el horario: el sitio dice «24 horas, 7 días» y el schema dice 09:00–17:00; ¿a qué hora se contesta de verdad?
- [ ] Revisar si hay desvío de llamadas o buzón, y quién contesta fuera de horario.
- [ ] Mirar el registro de llamadas perdidas del teléfono el 08 y 09-10 y comparar con las 8 llamadas del panel (menú Segmentos → «Medición»).
- [ ] Decidir si se baja la duración mínima de «Calls from ads» de 60 s a 30 s (lo cambia el dueño en Google Ads; no lo hace Claude).

## Paso C · Rafael: contar los clics en WhatsApp y teléfono (GTM + GA4)
Datos verificados del sitio: GTM `GTM-WLPJJD4J`, GA4 `G-26K0MDTFY1`, enlaces `wa.me`, `api.whatsapp.com` y un `tel:`. Nadie ha visto el contenedor de GTM.

1. En Google Tag Manager (contenedor `GTM-WLPJJD4J`) crear la variable «Click URL» (integrada) si no está activa.
2. Disparador «Clic en WhatsApp»: tipo *Solo enlaces*, se activa cuando `Click URL` contiene `wa.me` o `api.whatsapp.com`.
3. Disparador «Clic en teléfono»: tipo *Solo enlaces*, cuando `Click URL` empieza con `tel:`.
4. Dos etiquetas «Evento de GA4» hacia `G-26K0MDTFY1`: `click_whatsapp` (con el disparador 2) y `click_phone` (con el disparador 3).
5. Probar con «Vista previa» de GTM y DebugView de GA4: al pulsar cada botón debe aparecer el evento. Publicar solo después de probar.
6. En GA4 (Administrar → Eventos) marcar ambos como **evento clave**.
7. Vincular GA4 con Google Ads (cuenta de datos `203-550-4421`) e importar los eventos clave como conversiones.
8. Avisar al dueño: en el panel se verán como conversiones de la web, que hoy son 0.

**Qué mide y qué no:** cuenta clics en los botones, no conversaciones ni servicios concretados. Eso lo cubren los pasos D, E y F del plan, que necesitan aprobación expresa del dueño.

## Qué NO se toca desde el panel
- La etiqueta de Google de la cuenta de Ads dice «NO HAY DATOS»: la revisa Rafael en el sitio; no se pulsa «Terminar de configurar» ni «Conectar producto» sin aprobación del dueño.
- No se crea una propiedad nueva de GA4 ni se pulsa «Empezar a medir» (crearía una propiedad vacía).
