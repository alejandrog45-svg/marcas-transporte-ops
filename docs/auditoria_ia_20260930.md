# Auditoría de ubertransfer.cl con ChatGPT, Gemini y Meta AI (30-09-2026)

**Uso interno.** Contiene puntos débiles de seguridad del sitio: no publicar ni compartir fuera del equipo.
Hecha el 30-09-2026 entre 00:30 y 00:50 (hora de Chile). Las tres IAs recibieron **el mismo pedido** (URL, páginas a revisar, nuestras mediciones y la instrucción de separar VERIFICADO de SUPOSICIÓN). Cuentas del dueño: ChatGPT Plus, Gemini Plus y Meta AI, en conversaciones nuevas y sin datos sensibles.

## 1. Qué está medido por nosotros (evidencia propia)
| Hallazgo | Evidencia | Fuente |
|---|---|---|
| Portada lenta: 2,2–3,1 s por página | Auditoría desde GitHub, 4 páginas HTTP 200 (00:45) | `data/audit_latest.json` |
| **El retraso es del servidor, no de la red:** primer byte en 2,4–2,6 s (3 pruebas seguidas), conexión en 0,07 s | Medición con `curl` a las 00:36 | propia, una sola vez |
| La portada no envía cabeceras de caché (`Cache-Control`/`Expires` ausentes) | Cabeceras de la portada | propia |
| Faltan cabeceras de seguridad: HSTS, X-Frame-Options, X-Content-Type-Options, CSP y Referrer-Policy (solo hay Permissions-Policy) | Cabeceras de la portada | propia |
| `/wp-json/wp/v2/users` responde 200 (lista pública de usuarios de WordPress); `readme.html` y `license.txt` públicos | Códigos HTTP | propia |
| `xmlrpc.php` ya está bloqueado (403); `.env`, `.git/HEAD` y copias de `wp-config` dan 403; `wp-admin` redirige al login | Códigos HTTP | propia |
| Títulos largos: 92, 74 y 82 caracteres; description de 181 en `/servicio` | Auditoría | `data/audit_latest.json` |
| 39 imágenes sin lazy-load en la portada (13 y 10 en otras dos páginas) | Auditoría | idem |
| `/tarifas/` da 404 | Código HTTP | propia |
| HTTP→HTTPS y www→sin-www redirigen bien (301); `robots.txt` y `sitemap_index.xml` correctos | Códigos HTTP | propia |

**No medido (mi comprobación falló):** compresión gzip/brotli y HTTP/2.

## 2. Cómo se comportó cada IA
| IA | Acceso al sitio | Fiabilidad |
|---|---|---|
| **ChatGPT** | Dijo que no pudo recuperar el sitio de forma estable; usó una copia antigua de Google | **La más rigurosa.** No dio por verificadas nuestras cifras que no pudo reproducir, y marcó "no reproducido". Aclaró que GTM + gtag **no implica** duplicación por sí solo. |
| **Gemini** | Dijo tener "mediciones en vivo" | **Media.** Marca "VERIFICADO" cosas que solo repite de nuestros datos ("confirmo tu dato"). Afirma que la doble etiqueta "baja el rebote al 1–5 %" sin ver datos. |
| **Meta AI** | Dijo que un bloqueo anti-bot le impidió ver la portada | **Baja.** Aun así rotula como "VERIFICADO" cifras **incorrectas**: dio 87 y 78 caracteres para los títulos que medimos en 92 y 82. Cita precios ($18.000–$22.000) que **no están confirmados** por el dueño. Sugiere "ocultar /wp-json/", lo que puede romper plugins. |

Regla para usar estos textos: **una afirmación cuenta como verificada solo si aparece en la sección 1** o si el dueño/el sitio la confirma. Todo lo demás es hipótesis.

## 3. Lo que coincide entre las tres (y con nuestra medición)
1. Títulos y descriptions demasiado largos → acortar (≤ ~60 y ≤ ~155 caracteres).
2. `/tarifas/` en 404 → crear la página o redirigir.
3. Horario contradictorio entre el schema (09:00–17:00) y el texto (24/7).
4. Medición: GTM + gtag directo; faltan eventos claros de conversión (WhatsApp, llamada, formulario).
5. Lentitud y peso de imágenes (Divi + galerías).
6. Landing dedicada para tráfico de Google Ads, en vez de mandar todo a la portada.
7. Google Ads solo de Búsqueda, separada por intención (aeropuerto, corporativo, eventos, matrimonios).

## 4. Acciones consolidadas, en orden
| # | Acción | Por qué (evidencia) | Quién | Decisión del dueño |
|---|---|---|---|---|
| 1 | **Arreglar la lentitud del servidor**: revisar que la caché de página de LiteSpeed realmente sirva la portada; sin cabeceras de caché y con 2,4 s de espera, las imágenes no son el cuello de botella principal | Sección 1 (medición propia; **ninguna IA lo detectó**) | Quien administra el hosting / WordPress | Confirmar acceso |
| 2 | Verificar la medición **antes de tocar nada**: Tag Assistant + DebugView de GA4 para ver si `page_view` se dispara una o dos veces; luego dejar solo GTM y crear los eventos `click_whatsapp`, `click_phone`, `lead_submit` | ChatGPT acierta: dos etiquetas no siempre duplican | Rafael / quien tenga GTM | Ninguna |
| 3 | Unificar el horario (schema, texto y Perfil de Empresa) | Contradicción verificada | Rafael | **Sí: decidir el horario real.** Las IAs sugieren "24/7" pero es un dato pendiente del negocio |
| 4 | `/tarifas/`: redirigir a la sección de tarifas de la portada ahora, y crear la página real cuando haya tarifas confirmadas | 404 verificado. Ojo: Gemini dice que el menú apunta ahí; antes vimos que apunta a `/#tarifas`. **Comprobar haciendo clic** | Rafael | **Sí: tarifas** |
| 5 | Reescribir títulos y descriptions | Auditoría propia | Quien edite Rank Math | Revisar textos |
| 6 | Lazy-load, WebP y tamaños de imagen (excepto la imagen principal) | 39 imágenes sin lazy-load | Hosting/WordPress | Ninguna |
| 7 | Cabeceras de seguridad (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy) y limitar la lista pública de usuarios de `wp-json` (**no** desactivar wp-json completo) | Sección 1 | Hosting/WordPress | Ninguna |
| 8 | Probar en un celular real si `mystickyelements` y `wp-whatsapp` compiten por el clic; dejar un solo botón flotante | Gemini y Meta lo señalan; ChatGPT no. **Sin verificar** | Rafael | Ninguna |
| 9 | Landing para Ads con formulario arriba, sin menú de fuga, y mensaje de WhatsApp prellenado (sin inventar precios) | Consenso | Rafael + nosotros (borrador) | **Sí: promo de $5.000 vigente o no** |
| 10 | Ads de Búsqueda: negativas para la app (`app`, `aplicación`, `conductor`, `trabajar`); revisar la política de marcas de Google Ads por el nombre "Uber" antes de publicar | Gemini/Meta; **riesgo sin verificar** | Nosotros | Aprobar antes de publicar |

## 5. Lo que ninguna IA puede saber sin acceso
Indexación real (ChatGPT sospecha que las páginas internas no aparecen en Google: **sin verificar**), consultas y posiciones, Core Web Vitals de campo, versión de WordPress/Divi/plugins, configuración exacta de LiteSpeed, disparos reales de GTM/GA4, términos de búsqueda de Ads, Perfil de Empresa y llamadas reales. Todo esto depende del acceso de Rafael (Search Console, GA4, WordPress).

## 6. Incidente aparente de conectividad (retirado)
Entre 00:38 y 00:44 mis conexiones al sitio (`curl`/Python) y la herramienta de lectura web agotaron el tiempo, y llegué a pensar que el sitio estaba caído. **No lo estaba:** a las 00:45 el navegador del dueño lo cargó y GitHub midió las 4 páginas con HTTP 200. Lo más probable es que un cortafuegos bloqueó por un rato a clientes automáticos. Yo había hecho unas 30 consultas seguidas, algunas a rutas típicas de escáneres (`.env`, `.git`, `xmlrpc.php`), y las tres IAs consultaban el sitio a la vez. **Lección:** no repetir esos sondeos; para vigilancia usar la auditoría diaria y un monitor externo (UptimeRobot, pendiente de crear).

## 7. Revisión del PANEL por las tres IAs (30-09-2026, 01:00–01:15)
Se les dio la URL https://ubertransfer-ops.web.app/ y una descripción del proyecto. **Ninguna pudo abrir la página** con su herramienta (ChatGPT: "restricted URL"; Meta AI: "PAGE_NOT_FOUND"). Gemini dijo haber leído el HTML base. Meta AI reevaluó después con una captura que le pasó el dueño. Por eso todas partieron de la descripción y varias "verificaciones" no lo son.

| Propuesta | IA | Decisión | Motivo |
|---|---|---|---|
| Separar "puja de parte superior" del CPC real; mostrar ambos escenarios | las 3 | **Adoptada** | Selector de costo por clic: prudente (puja superior) o referencia (CPC medio de Google, 130 CLP). También corre sin frases marcadas |
| Embudo clic → contacto → reserva con costo por contacto y por reserva | ChatGPT, Gemini, Meta | **Adoptada, sin cifras inventadas** | Los porcentajes los escribe el usuario (vacíos por defecto) y están rotulados como SUPUESTO |
| Etiquetar cada dato: histórico, previsión de Google, simulación, supuesto | ChatGPT | **Adoptada** | Insignias en simulador, previsión y tabla |
| "Competencia" es de Google Ads, no SEO; volúmenes redondeados, no sumar | ChatGPT, Meta | **Adoptada** | Encabezado "Competencia (Ads)" y avisos |
| Campo numérico para el presupuesto además del deslizador | Gemini | **Adoptada** | Correcta: solo había deslizador |
| Botón para marcar las 10 frases de la previsión | Meta | **Adoptada** | Evita que el simulador parezca vacío |
| Filtro de intención de compra | Meta | **Adoptada** (heurística) | Coincidencias automáticas, avisado como tal |
| Aclarar qué mide "Consultar en vivo" y espaciar las consultas | ChatGPT, Meta | **Adoptada** | Texto explicativo y pausa de 30 s (cada consulta hace 3 solicitudes al sitio del cliente) |
| "Las verificaciones OK no garantizan resultados" | Meta | **Adoptada** | Texto ajustado a "verificaciones de datos" |
| Aviso de que más presupuesto no da más clics con solo esas frases | Gemini | **Adoptada, como inferencia** | Lo dice "probablemente" y cita la previsión de Google |
| Proteger el panel (noindex no es acceso) | las 3 | **Pendiente: Tarea 3** | Login real; ya se documentó en el panel que hoy es público |
| Tabla que se desborda en celular | Gemini | **Rechazada: falso** | Ya está en contenedor con scroll y pasa a tarjetas (verificado a 375 px) |
| Contraseña puesta en el código de la página | Gemini, Meta | **Rechazada** | Quedaría visible en el código fuente; no protege nada |
| Cloud Functions para autenticación | Meta | **Rechazada** | Exige plan de pago |
| Tasas inventadas (CTR 3–8 %, conversión 4 %, cierre 65 %, "cada negativa ahorra 15 %") | Meta | **Rechazada** | Rompe la regla de no inventar datos |
| Cambiar el nombre "UberTransfer" de inmediato | Gemini | **Rechazada como orden; anotada como riesgo** | Es la marca del cliente. Gemini afirma un "baneo vitalicio" sin sustento; se dejó como punto por verificar |
| Estacionalidad "picos en enero y julio" | Gemini | **No verificable** | Las 12 columnas mensuales del CSV vienen en 0 (Google no las entrega a cuentas sin gasto) |

**Un error propio detectado en esta ronda:** un parche mío borró por accidente las 4 tarjetas de resumen; la verificación "las tarjetas coinciden con la tabla" lo marcó como falla (`tarjetas ? / ?`) y se corrigió. Es un ejemplo de por qué existen esas verificaciones.
