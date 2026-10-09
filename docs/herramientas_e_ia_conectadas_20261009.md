# Herramientas e IAs conectadas en W: con la cuenta de Alejandro (inventario 09-10-2026)

Inventario de solo lectura. **No se abrió ningún archivo con secretos**: de los `.env` solo se listaron nombres
de variables; `SECRETOS\` y `varios txt\APIKEY.txt` no se abrieron. No se instaló nada.

## 1. IAs conectadas

| IA | Estado | Dónde | Uso |
|---|---|---|---|
| **Gemini API** (plan gratuito) | Conectada y en uso | Clave cifrada con DPAPI en `W:\PROYECTOS CUENTA ALEJANDROG45\_boveda\GEMINI_API_KEY.enc`; Secret `GEMINI_API_KEY` del repo | Redacta las sugerencias de IA del panel cada día, con validador de cifras. Respaldo entre modelos ante 503. |
| **Claude** (esta sesión, escritorio) | Conectada | Cuenta alejandrog45 | Desarrollo, revisión y verificación. No corre sin supervisión en GitHub (requeriría API de pago). |
| ChatGPT, Gemini Plus, Meta AI (webs) | Solo manual | Chrome del dueño | Flujo `consultas/` del repo; no tienen API en tus planes. |
| Otras claves de Gemini | Existen en los `.env` de `CabrasGO`, `PROYECTO SUSHI` y `DATA TRANSPORTE\Plataformas-anuncios-local` | Proyectos hermanos | No se tocaron. |

## 2. Herramientas y cuentas conectadas

| Herramienta | Estado |
|---|---|
| GitHub (`gh` de W:, cuenta `alejandrog45-svg`, permiso `workflow`) | Activa. Repos: `marcas-transporte-ops` (**PÚBLICO**), `Plataforma-anuncios` (privado), `data-transporte` (público), `rincon-sushi-app` (privado), `CabrasGO` (público). |
| Firebase CLI de W: (`W:\firebase-cli-alejandro\firebase-alejandro.cmd`) | Activa como `alejandrog45@gmail.com`, sesión aislada. |
| Google Ads API (solo lectura) | Activa vía Secrets de GitHub; cuenta 203-550-4421. |
| Chrome (extensión) | Sesión de Alejandro con Google Ads (3 cuentas), Apps Script, Cloud Console y el panel. |
| Search Console, GA4, GTM | **No conectados** (necesitan a Rafael). |
| Skills de la sesión útiles para el objetivo | `marketing-skills:ads`, `ad-creative`, `analytics`, `attribution`, `cro`, `copywriting`, `competitors`, `seo-audit`; `data:analyze`, `explore-data`, `statistical-analysis`. |
| Conectores sin autorizar | Amplitude, BigQuery, Hex, Canva, Slack, Notion, Linear, Figma y otros: no hacen falta hoy. |

## 3. El activo más valioso sin usar: `DATA TRANSPORTE`

Dashboard de **viajes y ventas reales** de una empresa de transfers de aeropuerto en Santiago, publicado por
GitHub Pages con datos agregados (sin nombres ni teléfonos: 0 y 0 en revisión automática), actualizado cada día.
Carpeta: `W:\PROYECTOS CUENTA ALEJANDROG45\DATA TRANSPORTE`; datos: `data/data.json`.

| Dato (05-05 a 07-10-2026) | Valor |
|---|---:|
| Viajes | 2.295 |
| Ingresos | $83.876.000 |
| Ticket promedio | $39.752 |
| Viajes por mes | may 401 · jun 466 · jul 395 · ago 431 · sep 502 |
| Hacia el aeropuerto / desde el aeropuerto / otro | 1.358 / 467 / 470 |
| Sectores con más viajes | Santiago Centro 226, Las Condes 220, Providencia 215, Ñuñoa 178, Quilicura 165 |

**Para qué sirve:** da el valor real de un servicio (ticket ≈ $39.752) y la demanda real por día, hora y sector. Con eso se puede
calcular el costo máximo razonable por contacto, alinear la campaña con la demanda y, cuando se anoten resultados, medir
cuántos clics terminan en servicio (`docs/medicion_conversiones_plan.md`).

**Hipótesis por verificar (no conclusiones):**
- La campaña apunta a Región Metropolitana, Rancagua, Los Andes y Viña del Mar, pero los 15 sectores con más viajes son comunas de Santiago.
  El término con más clics, «transfer de viña al aeropuerto», no tiene conversiones. Falta saber qué rutas se atienden (pendiente de Rafael).
- La demanda de servicio se concentra de madrugada (vuelos) y los clics llegan entre 08:00 y 13:00: reservar y viajar ocurren en
  momentos distintos, así que no se pueden comparar hora contra hora.
- **Pregunta abierta:** ¿ese negocio es el mismo de la campaña de UberTransfer? No se asume; el dueño debe confirmarlo antes de cruzar datos.

## 4. Riesgos de seguridad detectados

1. **`marcas-transporte-ops` es un repositorio público** y guarda en claro `data/google_ads_ubertransfer.json` (campañas, presupuesto,
   términos de búsqueda, estado de las llamadas). No contiene claves ni datos personales, pero sí información comercial. El panel
   publicado va cifrado, el repositorio no. Recomendación: pasarlo a **privado** (Actions sigue funcionando; el panel no depende de GitHub Pages).
2. `varios txt\APIKEY.txt` parece un archivo de claves en texto plano: conviene moverlo a la bóveda cifrada o borrarlo.
3. `SECRETOS\` (3 JSON) y los `.env` de otros proyectos (incluido uno con claves de pago): no se abrieron; confirmar que sus carpetas no se sincronizan ni se suben.
4. El token del Bridge de Apps Script ya no sirve (implementaciones archivadas el 09-10).

## 5. Qué conectar o construir para aumentar clics de forma permanente

| Prioridad | Qué | Quién |
|---|---|---|
| 1 | Pasar el repositorio a privado | Dueño |
| 2 | Confirmar si `DATA TRANSPORTE` es el mismo negocio y cargar sus agregados (por día, hora y sector) en el panel junto a Google Ads | Dueño confirma; Claude construye |
| 3 | Revisión semanal automática (IA sobre datos reales + historial): términos a excluir, horarios, presupuesto, calidad del tráfico | Claude |
| 4 | Libro de contactos y conversiones de WhatsApp/teléfono (plan A–F) | Dueño + Rafael |
| 5 | Conectar Search Console y GA4 | Rafael |

Regla que rige todo: **solo datos reales de Google Ads (o de la operación), nunca inventados**; la IA no cambia presupuesto,
pujas ni campañas.
