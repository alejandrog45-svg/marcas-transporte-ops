# Cómo saber cuántos clics terminan en servicio

Objetivo permanente: **más clics de calidad, con datos reales de Google Ads**. Un clic solo vale si termina
en un contacto y, mejor, en un servicio concretado. Hoy el panel mide hasta el clic; este plan cubre el resto.

## 1. Lo que está verificado hoy (09-10-2026, API de Google Ads + HTML del sitio)

| Dato | Valor real | Qué significa |
|---|---|---|
| Etiquetado automático | **Activado** | Cada clic trae su `gclid`: se puede unir clic y resultado. Es la pieza más importante y ya está. |
| Acciones de conversión | Solo **«Calls from ads»** (llamadas) | No hay conversiones de la web (WhatsApp, formulario). |
| Duración mínima de llamada | **60 s** | Una llamada más corta no cuenta como conversión. |
| Llamadas desde anuncios (08 y 09-10) | **8**: **7 perdidas** (`MISSED`) y 1 contestada de 18 s | Casi todas las llamadas no se atendieron; la única contestada duró menos de 60 s. Por eso hay 8 llamadas y 0 conversiones. |
| Sitio ubertransfer.cl | GTM `GTM-WLPJJD4J` y GA4 `G-26K0MDTFY1`; varios enlaces de **WhatsApp** con mensaje escrito (un solo número) y un enlace `tel:` | Los eventos de clic no están verificados: nadie ha visto el contenedor de GTM. |
| Conversiones registradas | **0** | Sin conversiones, el panel solo puede hablar de tráfico y costo, no de ventas. |

«Perdida» es la clasificación de Google; la causa (teléfono apagado, fuera de horario, desvío, la persona cortó antes)
**no la sabemos** y solo se puede ver en el teléfono real.

## 2. Qué es «concretar un servicio» (el embudo)

1. **Clic** en el anuncio → ya medido.
2. **Contacto**: llamada contestada, o clic en el botón de WhatsApp o de teléfono → se mide a medias (solo llamadas).
3. **Conversación / cotización** → ocurre dentro de WhatsApp o por teléfono: ninguna herramienta lo ve sola.
4. **Servicio concretado** → lo sabe solo el dueño o el conductor.

Los niveles 1 y 2 se pueden automatizar. El 3 y el 4 requieren que alguien registre el resultado.

## 3. Opciones, de más simple a más precisa (todas gratuitas)

| Paso | Qué se hace | Quién | Esfuerzo | Qué mejora |
|---|---|---|---|---|
| **A. Atender las llamadas** | Revisar el teléfono que reciben los anuncios (horario, desvío, quién contesta). Opcional: bajar la duración mínima de 60 s a 30 s en la acción «Calls from ads». | Dueño | Bajo | De 7 de 8 perdidas a contestadas; las llamadas válidas empiezan a contar. |
| **B. Detalle de llamadas en el panel** | Ya hecho: tarjeta «Medición» en Segmentos con cada llamada, su estado y duración (sin números de teléfono). | Hecho | — | Ver cuántas se pierden, día a día. |
| **C. Clics en WhatsApp y teléfono como conversión** | En GTM, un disparador sobre los enlaces `wa.me`, `api.whatsapp.com` y `tel:` que envíe los eventos `click_whatsapp` y `click_phone` a GA4; marcarlos como eventos clave e importarlos a Google Ads. | **Rafael** (administra el sitio, GTM y GA4) | Medio | Pasar de 0 conversiones a contactos web reales. Cuenta clics, no conversaciones. |
| **D. Libro de contactos en el panel** | Una tabla donde se anota cada contacto con su resultado: «concretado», «no» (y motivo) y, si quiere, el monto. Se guarda en Firestore, solo para cuentas autorizadas. El panel calcula la tasa de cierre por día y por franja horaria. | Claude construye; dueño anota | Medio | Responde «¿cuántos concretaron y cuántos no?» sin tocar el sitio. |
| **E. Unir cada servicio con su clic exacto (`gclid`)** | El sitio guarda el `gclid` y agrega un código corto al mensaje de WhatsApp («Ref: A7K2»); al anotar el resultado se usa ese código. La API de Google Ads (`click_view`, solo lectura) dice qué palabra clave, hora y dispositivo generó ese clic. | Rafael (sitio) + Claude | Alto | Saber qué términos y horas producen servicios reales, no solo clics. |
| **F. Subir los servicios concretados a Google Ads** | Importar conversiones de servicios concretados con su `gclid`, para que Google optimice hacia servicios y no hacia clics. | Dueño aprueba; requiere permiso de escritura | Alto | Pujas orientadas a resultados reales. **Cambia los datos de conversión de la cuenta: solo con aprobación expresa.** |

## 4. Orden recomendado

1. **A** esta semana: es lo que más pesa hoy (casi todas las llamadas se pierden) y no cuesta nada.
2. **C** pidiéndoselo a Rafael: es el vacío más grande (cero conversiones de la web).
3. **D** construido por nosotros: da la respuesta directa a «cuántos concretaron».
4. **E** y **F** cuando existan C y D y haya al menos unas semanas de datos.

Ningún paso cambia presupuesto, pujas ni anuncios.

## 5. Privacidad

- No se guardan números de teléfono ni nombres; las llamadas se registran con fecha, duración y estado.
- El `gclid` y los resultados anotados viven solo en Firestore (acceso restringido a las cuentas autorizadas), nunca en el repositorio.
- Antes del paso E conviene confirmar con quien lleva lo legal qué aviso de privacidad necesita el sitio.

## 6. Decisiones pendientes

- Dueño: ¿se revisa el teléfono de los anuncios (paso A)? ¿Se baja la duración mínima a 30 s?
- Dueño: ¿se construye el libro de contactos (paso D)? ¿Quién anotaría los resultados?
- Rafael: acceso a GTM/GA4 para el paso C.
