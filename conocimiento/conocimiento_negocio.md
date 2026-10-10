# Conocimiento del negocio — UberTransfer.cl
Actualizado: 2026-09-29. Datos verificados en el sitio; lo demás está marcado como pendiente.

## Verificado (auditoría directa)
- Sitio: WordPress + Divi + Rank Math + LiteSpeed (Apache, PHP 8.3). Dominio canónico `https://ubertransfer.cl/` (www → redirige).
- Marca: "UberTransfer — Transporte Ejecutivo". Tipo schema: TravelAgency.
- Servicios en la home: aeropuerto, transporte de pasajeros (RM e interurbano), turismo, corporativo, compartidos (rutas fijas, tarifa por pasajero con una maleta).
- Contacto: WhatsApp/tel +56 9 4996 9267, correo cotizaciones@ubertransfer.cl. Oferta vigente: $5.000 de descuento en ida y retorno.
- Sitemap: 4 páginas (inicio, nosotros, servicio, contacto). `/tarifas/` = 404; "Tarifas" es ancla `/#tarifas`.
- Medición: GTM-WLPJJD4J y gtag G-26K0MDTFY1 presentes (posible duplicidad).
- Incoherencia: schema dice 09:00–17:00; el texto dice atención 24/7.

- Auditoría automática (repo `ubertransfer-ops`): titles de 74–92 car. en nosotros/servicio/contacto, description de 181 en servicio, imágenes sin lazy-load (39 en home). Alt vacío no se cuenta como error (decorativas).

## Propiedad y accesos (2026-09-29)
- El sitio `ubertransfer.cl` pertenece a Rafael, hermano del dueño del proyecto. Hosting y DNS en cPanel (`ns1/ns2.cpanelhost.cl`). Una tercera persona administra las campañas de Google Ads de Rafael.
- Sin etiqueta ni TXT de verificación de Google en el sitio; la propiedad de GSC del dominio quedó añadida con `alejandrog45@gmail.com` pero sin verificar.
- Cuenta de Google para todo el proyecto: `alejandrog45@gmail.com`. La cuenta `ferreteriaoviedo.elmanzano@gmail.com` se usa solo para GitHub.
- Google Ads propia `926-538-5719`, solo investigación (Planificador). Volúmenes: "transfer aeropuerto santiago" y "taxi aeropuerto santiago" ~1 mil–10 mil búsquedas/mes, competitividad alta, puja ~270–970 CLP por clic. Detalle en `docs/keywords_borrador_20260929.md`.
- Auditoría 2026-09-29: home lenta (3,24 s).


## Lo que el sitio publica hoy (verificado el 30-09-2026 con el HTML real; `data/inspeccion_sitio_latest.json`)
Son datos **publicados en el sitio**, no confirmados por el dueño para anuncios.
- **Contacto:** solo enlaces `wa.me` (con mensaje prellenado), `tel:+56949969267` y correos cotizaciones@ y gerencia@. **No hay ningún formulario.**
- **Oferta visible:** "$5.000 de descuento en ida y retorno" en las 4 páginas.
- **Tarifas por horario (portada):** HORARIO ALTA 07:30–18:00 y HORARIO BAJA 19:30–06:00.
- **Precios en la FAQ de /contacto:** aeropuerto–centro "suele variar de $18.000 a $22.000"; Terminal Pajaritos–Maipú "$19.000 aprox.".
- **Flota nombrada en la portada:** Carnival, Sorento, Rio y Mercedes Benz. **Servicio "Pet Friendly"** en /servicio.
- **Horario:** el texto dice atención "las 24 horas, los 7 días"; el schema (`openingHours`) dice 09:00–17:00. Sigue PENDIENTE de decisión del dueño.
- **Menú "Tarifas"** apunta a `/#tarifas`; `/tarifas/` da 404.
- **Schema (JSON-LD):** TravelAgency; sin teléfono, dirección ni zona de servicio (`areaServed`).
- **Medición:** GTM-WLPJJD4J y gtag G-26K0MDTFY1; se detectó además una etiqueta de Meta/Facebook (`facebook.com/tr`). Sin versión en inglés (sin hreflang).
- **Imágenes de la portada:** 39 (30 PNG), 0 con lazy-load, 23 sin alt.

## Registro de datos pendientes (valor · fuente · fecha de verificación)
| Dato | Valor | Fuente | Verificado | Estado |
|---|---|---|---|---|
| Horario real | — | dueño | — | PENDIENTE |
| Tarifas para anuncios | — (el sitio publica rangos en la FAQ) | dueño | — | PENDIENTE |
| Promo $5.000 vigente | publicada en el sitio | dueño | — | PENDIENTE de confirmar |
| Rutas y comunas atendidas | — | dueño | — | PENDIENTE |
| Nombre "Uber" y política de marcas de Google Ads | — | dueño/asesor | — | POR VERIFICAR |

## Pendiente de confirmar con el dueño
Horario real, comunas y rutas atendidas, tarifas, flota, estado de Google Business Profile y Search Console, conversión principal.

## Decisiones tomadas
- No migrar el sitio; agregar capa de automatización (Cloudflare, GitHub Actions, Firebase Spark, UptimeRobot).
- Google Ads: Search controlado, no Performance Max, hasta tener conversiones fiables.
- Claude solo detecta y propone; una persona aprueba gasto y publicación.
- Repo propio `oviedoem/ubertransfer-ops` (privado), separado del código de la ferretería. Histórico en `data/`.
- Sin credenciales en el repositorio: solo secretos de GitHub.

## Plan vigente
`docs/plan_ubertransfer_v2.html`

## Decisiones del panel (30-09-2026)
- «Todas las funciones en línea» = por etapas: primero que todo funcione y persista en la URL publicada (sin costo ni login); después nube/Firestore junto con el login. No revertir sin pedido del dueño.
- El favicon va en línea (data-URI SVG); no se añade `favicon.ico`.
- Estado HTTP de ubertransfer.cl: el navegador no puede leerlo (sin CORS); se declara y se usa el HTTP de la auditoría del servidor. No volver a intentar lectura CORS.
- El texto «31 días» de la comparación con Google es intencional (período de la previsión 1–31 oct); no depende del campo Días.
- Acceso al panel: Google (Firebase Auth) + reglas de Firestore por correo: alejandrog45@gmail.com y alimentosaltoque76@gmail.com (Rafael). Los correos viven solo en firestore.rules, no en la página pública.
- Formato de precios del panel: chileno, $1.000 (punto de miles, signo $), función money().
- Decisión del dueño (Rafael, 30-09): la campaña es de Búsqueda; no campaña inteligente ni Máximo rendimiento. Quiere sumar temas de eventos privados, matrimonios y transporte corporativo (aún sin datos de Google ni confirmación de servicio/tarifas). Detalle en docs/recomendaciones_rafael_20260930.md.
- El negocio NO es solo aeropuerto (dueño, 30-09): el sitio ofrece traslados corporativos (empresas, reuniones, conferencias, eventos de negocios), bodas/graduaciones/celebraciones, turismo, compartidos, privados, fuera de Santiago y Pet Friendly. Horario de tarifas visto en el sitio: ALTA 07:30–18:00, BAJA 19:30–06:00 (franjas de tarifa, sin confirmar). Promo: $5.000 de descuento por ida y retorno. Pago: Webpay/QR.
- Demanda medida en Google (Chile, sept 2025–ago 2026): «transfer matrimonios» 10–100/mes ($274–$1.007 por clic), «transporte corporativo» 10–100/mes ($601–$2.093). Aeropuerto: 1.000–10.000. Datos en data/keyword_planner_rubros_20260930.json.
- Tarifas por horario (ubertransfer.cl, confirmado por el dueño): ALTA 07:30–18:00 y BAJA 19:30–06:00, precios distintos; los tramos 18:00–19:30 y 06:00–07:30 no tienen tarifa indicada (PENDIENTE Rafael). El schema del sitio (09:00–17:00) contradice el «24 horas, los 7 días».
- Flota vista en aereostar.cl/nuestra-flota: Kia Sorento, Kia Gran Carnival, Mercedes Vito, Kia Sonata (todas con «6 pasajeros, Van, 2020», dato dudoso para la Sonata). No usar capacidades en anuncios hasta confirmarlas. aereostar.cl y ubertransfer.cl son ambas de Rafael: coordinar frases para no competir entre sí.
- Regla de coordinación (propuesta, pendiente de Rafael): una frase de Google pertenece a una sola marca (Aereostar o UberTransfer); la otra la lleva como negativa. Evita competir entre sí y la política de doble publicación de Google. Detalle: docs/coordinacion_aereostar_ubertransfer.md.
- Política de Google verificada (30-09): «Unfair advantage» prohíbe más de un anuncio del mismo negocio en una misma ubicación de anuncio (aclaración abril 2025), exige valor distinto por destino y avisa 7 días antes de suspender. Marcas: como palabra clave no se restringe; en el texto del anuncio puede restringirse tras reclamo del titular. MCC: vincular no borra historial; sirve para visibilidad, no como escudo. Fiabilidad de las IAs en esta consulta: ChatGPT alta, Meta media, Gemini baja/media.
- Registro de marcas (INAPI, consulta pública 30-09-2026): UBERTRANSFER y UBER TRANSFER no figuran; UBER está registrada por Uber Technologies, Inc. en Chile (clases 39 y 42; 12, 39, 42 y 9; 25 y 35); AEREOSTAR no figura. Riesgo: reclamo de Uber sobre el uso de «Uber» en textos de anuncios y posible oposición si se registra «UberTransfer». Decisión pendiente del dueño con abogado de propiedad industrial.
- Panel de Aereostar (30-09): https://ubertransfer-ops.web.app/aereostar/ — separado del de UberTransfer para medir cada marca por su lado (mismos accesos, datos propios). Sin campañas. No se inventan teléfono, tarifas ni horarios de Aereostar: figuran como PENDIENTE hasta que Rafael los confirme.
- Auditoría técnica de aereostar.cl (30-09, solo lectura): 11 páginas, todas responden 200 y rápido (0,3–0,8 s; UberTransfer tarda más). Fallas repetidas: sin meta description en las 11, títulos demasiado largos (79–105 car.), home sin H1, /portfolio/ con dos H1 y páginas del sitemap que parecen de la plantilla del tema (a confirmar con Rafael). Sí tiene página /tarifas/ (200), a diferencia de UberTransfer.
- Centro de Comando (E:\CONOCIMIENTO DEL NEGOCIO): hub de Ferretería Oviedo; no registra UberTransfer/Aereostar. Este proyecto se mantiene independiente (sin mezclar código, datos ni credenciales). Detalle: conocimiento/centro_comando.md.

## Decisión 2026-10-10: leyenda de la Auditoría
- PENDIENTE en la Auditoría = dato o decisión externa (lista fija `BIZ`), no un error del panel. La leyenda lo explica y remite al bloque de pendientes. No revertir sin pedido del dueño.
- Medición (10-10): pasos A y C listos en `docs/pasos_medicion_rafael_y_dueno.md`; D (libro de contactos) y F (subir conversiones) requieren aprobación expresa del dueño. PENDIENTE se muestra en ámbar en la Auditoría.

## Decisiones del 10-10-2026 (sesión de nube; no revertir sin pedido del dueño)
- Campañas de Google Ads: SOLO SE LEEN. Nunca pausar, activar, editar ni crear (orden del dueño).
- Aereostar: cuenta real de Ads 548-530-8262, campaña única «Campaign #1» (ID 24331409273), activa; sitio aereostar.cl ACTIVO. Panel propio, mismos 11 menús que UberTransfer.
- Identidad visual: UberTransfer = rojo `#ed1c24` + negro + verde; Aereostar = negro `#0b0b0b` + naranja `#e96712`/`#f29812` + amarillo `#f8e71d` (tomado del logo y de aereostar.cl). Logo de Aereostar en `docs/archivo/logo/logoaereostar.png`.
- Los dos paneles son PWA instalables, con insignia de versión «AG · v.N» y aviso de actualización; Aereostar bajo `/aereostar/`.
- Objetivo permanente: más clics sin subir costos, con datos reales; propuestas en `docs/mejoras_clics_sin_subir_costos.md`.
