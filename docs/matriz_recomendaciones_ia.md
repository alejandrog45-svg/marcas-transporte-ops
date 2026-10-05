# Matriz de recomendaciones de ChatGPT, Gemini y Meta AI: qué es viable y en qué estado está

**Uso interno** (incluye puntos débiles de seguridad del sitio). Preparada el 30-09-2026.
**Fuentes revisadas completas:** (1) primera consulta de ideas de campaña (ChatGPT y Gemini); (2) auditoría del sitio con las 3 IAs; (3) revisión del panel con las 3 IAs, sus 3 reportes `.md` (Meta, Gemini y ChatGPT) y la segunda respuesta de Meta leyendo el código real.
**Cómo se comprobó cada punto:**
- **HTML real del sitio**, leído por GitHub el 30-09-2026 04:17 UTC (`data/inspeccion_sitio_latest.json`, 4 solicitudes normales).
- **Mediciones propias** (cabeceras, tiempos) y **auditoría diaria** (`data/audit_latest.json`).
- **Pruebas del panel** en local y en la URL publicada.

Leyenda de estado: ✅ hecho · 🟡 pendiente de una persona · 🔵 depende de acceso o de una campaña real · ❌ rechazado · ⚠️ no confirmado

## A. Sobre el sitio ubertransfer.cl (el sitio es de Rafael)
| # | Recomendación | Quién la dijo | ¿Viable? | Evidencia comprobada | Estado y responsable |
|---|---|---|---|---|---|
| A1 | Acortar títulos (~60 caracteres) | las 3 | Sí | Títulos: portada 62, nosotros 92, servicio 74, contacto 82 | 🟡 Rafael (Rank Math) |
| A2 | Acortar descriptions (~155) | las 3 | Sí | Portada 155 (bien); nosotros **175**, servicio **181**, contacto **159**. Son 3 páginas, no solo `/servicio` | 🟡 Rafael |
| A3 | Arreglar `/tarifas/` (404) | las 3 | Sí | `/tarifas/` da 404, pero **el menú apunta a `/#tarifas`** (ancla), no a la ruta rota. Gemini se equivocó al decir que el menú da 404 | 🟡 Rafael: redirigir 301 o crear página. La página real necesita tarifas confirmadas |
| A4 | Unificar el horario (schema vs texto) | las 3 | Sí, **pero el horario lo decide el dueño** | Schema (`openingHours`) dice 09:00–17:00 en las 4 páginas; el texto dice "24 horas, los 7 días" en las 4. Además la portada publica "Tarifas por horario" (07:30–18:00 alta / 19:30–06:00 baja) | 🟡 Rafael. Las IAs sugieren "24/7" pero no se aplica sin su decisión |
| A5 | Quitar la doble etiqueta GTM + gtag | las 3 | **Solo después de verificar** | Presentes `GTM-WLPJJD4J` y `G-26K0MDTFY1` con gtag directo. Que estén juntas no prueba que cuenten doble. ChatGPT acierta; Gemini ("rebote 1–5 %") no tiene datos | 🔵 requiere acceso a GTM/GA4 y Tag Assistant |
| A6 | Medir clics en WhatsApp, teléfono y formulario | las 3 | Sí, **adaptado** | **El sitio no tiene ningún `<form>`** (0 en las 4 páginas). Contacto = enlaces `wa.me` (con mensaje prellenado), `tel:` y `mailto:`. No aplica `lead_submit` ni página "gracias" | 🔵 crear `click_whatsapp`, `click_phone`, `click_email` |
| A7 | Activar lazy-load | las 3 | Sí | 0 de 39 imágenes con `loading="lazy"` en la portada (0 en las otras 3 páginas) | 🟡 hosting/WordPress (excluir la imagen principal) |
| A8 | Convertir imágenes a WebP, `srcset` y tamaños | las 3 | Sí | Portada: **30 PNG**, 6 JPG/JPEG, 2 WebP; sin `srcset`; 16 sin width/height | 🟡 Rafael |
| A9 | Textos alternativos (alt) | ChatGPT, Gemini | Sí | 23 de 39 imágenes de la portada sin alt; 13/13, 10/10 y 8/8 en las otras páginas | 🟡 Rafael |
| A10 | (Hallazgo propio, ninguna IA lo vio) Servidor lento y sin caché | — | Sí | Primer byte 2,4–2,6 s (conexión 0,07 s); sin `Cache-Control`; portada 2,2–3,1 s desde GitHub (6,07 s en una lectura) | 🟡 quien administre el hosting (caché de LiteSpeed) |
| A11 | Unificar los botones de WhatsApp (`mystickyelements` + `wp-whatsapp`) | Gemini, Meta | Plausible | Ambos plugins están en el HTML; hay "Ejecutiva de ventas 1/2 En línea" y varios enlaces `wa.me`. Impacto en el clic **no medido** | 🟡 probar en un celular real |
| A12 | Datos estructurados: teléfono, dirección, zona de servicio | Meta, ChatGPT | Sí | JSON-LD (TravelAgency) **sin** teléfono, dirección ni `areaServed` en las 4 páginas; `sameAs` solo en 3 internas | 🟡 Rafael (Rank Math) |
| A13 | Cabeceras de seguridad (HSTS, X-Frame-Options, nosniff, CSP, Referrer-Policy) | las 3 | Sí | No aparecen en la portada (solo Permissions-Policy) | 🟡 hosting |
| A14 | Restringir `/wp-json/wp/v2/users` (lista pública de usuarios) | Meta | Sí, **sin desactivar wp-json completo** | Responde 200. `xmlrpc.php` ya está bloqueado (403) | 🟡 hosting/WordPress |
| A15 | Correos en `mailto:` expuestos | Meta | Riesgo bajo | Hay dos: cotizaciones@ y gerencia@ | 🟡 opcional |
| A16 | Landing dedicada para Google Ads | las 3 | Sí | La portada mezcla 4 servicios | 🟡 Rafael + nosotros (borrador) |
| A17 | Páginas SEO por ruta (Las Condes, Viña, Valle Nevado…) | Gemini, ChatGPT | Parcial | Rutas y comunas **no confirmadas**. ChatGPT advierte no crear páginas casi iguales cambiando solo la comuna | 🟡 Rafael confirma rutas |
| A18 | Versión en inglés y palabras clave en inglés | Gemini | Requiere crear la versión | Sin `hreflang` ni páginas en inglés | 🔵 decisión del dueño |
| A19 | Indexación de las páginas internas | ChatGPT (sospecha) | No verificable | ChatGPT no las encontró en su búsqueda. `robots` = index y el sitemap existe | 🔵 Search Console |
| A20 | Revisar el nombre "Uber" (política de marcas) | Gemini | Riesgo por verificar | Gemini exagera ("baneo vitalicio", "cambiar de inmediato") sin sustento | 🟡 decisión del dueño/asesor |
| A21 | Píxel de Meta/Facebook (**hallazgo nuevo**) | ninguna | Verificar | Aparece `facebook.com/tr` en las 4 páginas | 🟡 confirmar si se usa y si hay aviso de cookies |
| A22 | Aviso de que "Uber Tran sfer" está partido | ChatGPT | ⚠️ no confirmado | Aparece "Tran sfer" en el texto extraído; puede ser un efecto del diseño (letras en etiquetas separadas) | 🟡 mirar la página |
| A23 | Mover el "QR para pagar rápido" del pie | Gemini | Es opinión | Verificado que existe en el pie de todas las páginas | 🟡 decisión de Rafael |
| A24 | Precios en la FAQ | Meta | Verificado | `/contacto`: "aeropuerto–centro suele variar de $18.000 a $22.000" y "Pajaritos–Maipú $19.000 aprox." | 🟡 Rafael confirma antes de usarlos en anuncios |

## B. Sobre la campaña de Google Ads (consulta 1 y auditoría)
| # | Recomendación | Quién | ¿Viable? | Estado |
|---|---|---|---|---|
| B1 | 1 campaña con grupos por intención (aeropuerto, eventos/matrimonios, corporativo, compartido) | ChatGPT, Gemini, Meta | Sí. El sitio **sí ofrece** servicios compartidos (título "Servicios Compartidos") | ✅ el Borrador arma los grupos |
| B2 | Empezar con concordancia de frase y exacta | ChatGPT | Sí | ✅ el Borrador genera `"frase"` y `[exacta]` |
| B3 | Solo Búsqueda; sin Display ni socios | ChatGPT | Sí | ✅ Borrador y paso 5 del Recorrido |
| B4 | 20 y 30 palabras nuevas | ChatGPT, Gemini | Parcial: sin volumen hasta consultarlas en el Planificador. Algunas dependen de servicios no confirmados (silla de bebé, "pago a 30 días", Viña, Valle Nevado) | 🟡 revisar con el dueño y consultar el Planificador |
| B5 | Palabras negativas iniciales | ChatGPT, Gemini, Meta | Sí, con cuidado ("trabajo" y "bus" podrían excluir clientes reales) | ✅ 20 negativas editables, con advertencia |
| B6 | Títulos ≤30 y descripciones ≤90 | ChatGPT | Sí | ✅ verificados y revisor de largo en el Borrador. Los textos deben ser ciertos |
| B7 | Errores comunes de principiante | ChatGPT | Sí | ✅ cubiertos en Guía, Recorrido y embudo |
| B8 | Revisión semanal de 15 min (términos de búsqueda 5, presupuesto/cuota 3, ubicaciones 3, anuncios 4) | Gemini | Sí, cuando exista campaña | 🔵 sumar al Recorrido como rutina |
| B9 | Negativas de marca ("app", "conductor", "trabajar en uber") | Gemini, Meta | Sí, **específicas**. Una negativa "uber" a secas es riesgosa por el propio nombre | ✅ "app", "aplicación", "conductor uber" |
| B10 | Extensiones: sitelinks y llamada | Meta | Sí | ✅ paso 10 del Recorrido. El número verificado es +56 9 4996 9267 |
| B11 | Callouts "Autorizado AP", "Pago a bordo", "24/7" | Meta | ❌ no confirmados y "24/7" se contradice con el schema | ✅ advertido en el Recorrido |
| B12 | Estructura "SKAG" | Meta | ❌ práctica obsoleta | ❌ |
| B13 | Módulo "términos de búsqueda → negativas" y ROAS | ChatGPT | Sí, con una campaña real | 🔵 futuro |

## C. Sobre el panel (revisión de las 3 IAs)
| # | Recomendación | Quién | Estado |
|---|---|---|---|
| C1 | La puja de parte superior no es el CPC real; mostrar ambos escenarios | las 3 | ✅ selector de costo por clic; **por defecto el CPC medio de Google** y el otro escenario siempre visible |
| C2 | Embudo clic → contacto → reserva → costo, sin inventar tasas | las 3 | ✅ los porcentajes los escribe el usuario, vacíos por defecto |
| C3 | Rotular el tipo de dato (histórico, previsión, simulación, supuesto) | ChatGPT, Meta | ✅ insignias |
| C4 | "Competencia" es de Google Ads; volúmenes redondeados, no sumar | ChatGPT, Meta | ✅ |
| C5 | Campo numérico de presupuesto | Gemini | ✅ |
| C6 | Marcar las 10 frases / evitar estado vacío | Meta | ✅ botón, y **desde la primera visita** vienen marcadas |
| C7 | Filtro de intención de compra | Meta | ✅ heurística avisada como tal |
| C8 | Aclarar qué mide "Consultar en vivo" y espaciar las consultas | ChatGPT, Meta | ✅ texto y pausa de 30 s |
| C9 | "16/16 no garantiza resultados" | Meta | ✅ |
| C10 | Aviso de saturación de tráfico | Gemini | ✅ como inferencia |
| C11 | "Empieza aquí" en 5 pasos | ChatGPT | ✅ en la Guía |
| C12 | `noarchive` | Meta (reporte .md) | ✅ |
| C13 | Neutralizar fórmulas en el CSV exportado | ChatGPT | ✅ |
| C14 | Revisar inyección de HTML | ChatGPT | ✅ probado: una frase con `<img onerror>` se muestra como texto y no se ejecuta |
| C15 | Buscar claves en el código | ChatGPT | ✅ 0 claves, tokens ni datos personales (Meta AI lo confirmó leyendo el código) |
| C16 | Contraste WCAG AA | ChatGPT, Meta | ✅ medido: 5,2 a 14,4 (mínimo exigido 4,5) |
| C17 | Botón "Copiar" sin nada que copiar | Meta | ✅ avisa |
| C18 | Proteger el panel con acceso real | las 3 | 🟡 **Tarea 3**. Hoy es público y se advierte dentro del panel |
| C19 | Escenarios Conservador/Base/Optimista | ChatGPT | ✅ tabla en el Simulador: 3 referencias reales de CPC (puja alta, puja baja, CPC medio de Google) ordenadas de mayor a menor, con su origen visible. Contactos/reservas solo con los supuestos del dueño (vacío = "—") |
| C20 | Grupos "aeropuerto → ciudad / ciudad → aeropuerto" | ChatGPT | ✅ filtro "Dirección" por el texto de la frase: 23 hacia el aeropuerto, 7 desde, 140 sin dirección (=170). Rutas/comunas siguen sin confirmar |
| C21 | Guardar filas por página; atajos de teclado; zebra rows | Meta | ✅ filas por página recordadas; `/` busca, `←` `→` páginas; filas alternas; ⓘ con ayuda en las cabeceras (también al tocar en celular) |
| C22 | Aviso de estacionalidad | Gemini | ✅ hecho con **Google Trends real** (consultado 30-09-2026 desde la interfaz oficial, 3 solicitudes; `data/trends_estacionalidad.json`): índice mensual normalizado por año 2022–2025. Enero 142, febrero 134 y diciembre 112 son los picos; marzo–noviembre 84–97. Contrastado con ChatGPT (coherente; límites y propuesta de presupuesto marcada como sin verificar). Series oficiales de pasajeros (JAC/Nuevo Pudahuel) inaccesibles a bots: no usadas. `pytrends` está archivado (no usar) |

## D. Afirmaciones de las IAs que resultaron **falsas o sin base**
| IA | Afirmación | Realidad |
|---|---|---|
| Gemini | "La tabla se desborda en el celular" | Está en un contenedor con scroll y pasa a tarjetas (medido a 375 px) |
| Gemini | "El menú de Tarifas da 404" | El menú apunta a `/#tarifas` |
| Gemini | "La doble etiqueta baja el rebote a 1–5 %" | Sin datos de GA4 no se puede saber |
| Gemini | "Baneo vitalicio por usar Uber" | Sin sustento; es un riesgo a revisar, no una orden |
| Meta | "Títulos de 87 y 78 caracteres" | Son 92 y 82 |
| Meta | "El schema tiene el teléfono sin espacio" | El schema **no** tiene teléfono |
| Meta | "instagram-feed vacío" | Hay publicaciones de Instagram en el HTML |
| Meta | "Sin enlace `tel:`" | Existe `tel:+56949969267` en las 4 páginas |
| Meta | "H1 y H2 duplicados" y "FAQ idéntico dos veces" | No hay encabezados repetidos |
| Meta (1.ª ronda) | La tabla del panel sin paginación, sin selección masiva, sin campo de presupuesto, sin etiquetas de puja | Todo existe (lo reconoció al leer el código) |
| Meta | "Conversión 4 %, cierre 65 %, CTR 3–8 %, cada negativa ahorra 15–30 %" | Cifras inventadas, rechazadas |
| Meta, Gemini | Contraseña escrita en el código de la página | No protege nada: se ve en el código fuente |
| Meta | "Cloud Functions para autenticar" | Exige plan de pago |

## E. Lo que queda abierto y qué haría falta para cerrarlo
1. **Acceso de Rafael a GA4/Search Console:** indexación (A19), doble medición real (A5), Core Web Vitals de campo, términos de búsqueda.
2. **Decisiones del dueño:** horario (A4), tarifas y precios de la FAQ (A3, A24), promo de $5.000, nombre "Uber" (A20), rutas y comunas (A17), versión en inglés (A18).
3. **Hosting:** caché del servidor, cabeceras y usuarios de wp-json (A10, A13, A14).
4. **Panel privado con login:** Tarea 3.
5. **Estacionalidad real:** Google Trends (gratis), pendiente.
6. **Acceso al sitio desde este PC:** el cortafuegos del hosting parece haber bloqueado la IP del dueño por mis consultas de las 00:38. No repetir sondeos; esperar a que se libere.

## F. Auditoría completa de ChatGPT (30-09-2026, sobre el repo y el panel publicado)
Informe íntegro: `docs/auditoria_chatgpt_completa_20260930.md` (uso interno). Cada hallazgo se **verificó en el código** antes de aplicarlo.
| # | Hallazgo | ¿Confirmado? | Estado |
|---|---|---|---|
| F1 | Panel público sin login | Sí (`noindex` no protege) | 🟡 Tarea 3; el dueño pidió dejarla para el ÚLTIMO |
| F2 | `collect_urls()` traga errores y la auditoría "termina bien" con 0 páginas | Sí | ✅ `AuditError`, estado de robots y de cada sitemap en `discovery`, no se pisa `audit_latest.json`, código de salida 1 + prueba |
| F3 | GA4 `sessions` = conteo del evento `session_start` | Sí | ✅ ahora se pide la métrica `sessions` (2.ª consulta); `session_start_events` se guarda aparte + prueba |
| F4 | Simulador extrapola linealmente sobre la previsión de Google | Sí (10.000 CLP/día → 2.356 vs ≈1.100) | ✅ aviso rojo "Extrapolación no validada" (>15 % sobre la previsión), rótulos "cálculo, no previsión" y fila fija con la previsión oficial |
| F5 | 17/17 mide consistencia interna, no exactitud comercial | Sí | ✅ verificaciones en 3 bloques; el 3.º lista lo pendiente de negocio (horario, tarifas, promo, rutas, marca, conversiones, GSC/GA4) |
| F6 | El job SEO se omite sin error visible | Sí | ✅ `::warning` en Actions + `data/seo_status.json` + el panel dice "el flujo SEO diario no está extrayendo datos". No se abre Issue diario (sería ruido) |
| F7 | Permisos amplios en workflows | Parcial | ⚪ revisado: `contents: write` solo donde se guarda histórico; `issues: write` solo en SEO; sin cambio |
| F8 | Acciones sin fijar por SHA, `firebase-tools@15` flotante | Sí | ✅ SHAs de checkout v4.4.0, setup-python v5.6.0, setup-node v4.4.0; `firebase-tools@15.19.0` |
| F9 | `no-cache` en todo el hosting | Verdadero pero sin efecto: el panel es UN archivo HTML inline | ⚪ sin cambio (solo `index.html` y `version.json`; cachearlos rompería la verificación de versión) |
| F10 | El auditor no cubre cabeceras, OG, srcset, enlaces rotos, etc. | Sí | 🟡 P1: integrar el inspector de contenido al ciclo semanal (sin sondeos agresivos) |
| U3 | Renombrar "Optimista" | Sí | ✅ escenarios con nombre por origen: Puja alta (conservador), Puja baja, CPC de la previsión de Google |
| U4 | Botón "Restaurar escenario inicial" | Sí | ✅ |
| U1/U2/U6/U7 | Etiquetas de origen en cada cifra, fecha de vigencia por puja, diferenciar ideas de IAs, estado en Mejoras del sitio | Sí | 🟡 pendiente (mejora de producto) |
| U8/P2 | Pruebas E2E del panel (375/820/1440) | Sí | 🟡 pendiente; hoy se prueba a mano en el navegador |
