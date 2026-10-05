# Tu parte manual (una sola vez, ~60–90 min)

Son pasos que exigen tu identidad; el sistema no puede hacerlos por ti. **Nunca pegues claves en el chat ni en el código.**

## 1. Cuenta de servicio de Google (gratis)
1. https://console.cloud.google.com → crear proyecto `ubertransfer-ops`.
2. *APIs y servicios → Biblioteca*: habilitar **Google Search Console API** y **Google Analytics Data API**.
3. *IAM → Cuentas de servicio → Crear*: nombre `ubertransfer-reader` (sin roles del proyecto).
4. *Claves → Agregar clave → JSON*: se descarga un archivo. Copia el correo `...@...iam.gserviceaccount.com`.

## 2. Dar acceso de solo lectura a esa cuenta
- **Search Console** (search.google.com/search-console): propiedad de `ubertransfer.cl` → *Configuración → Usuarios y permisos → Agregar usuario* → el correo de la cuenta de servicio, permiso **Restringido**.
- **GA4** (analytics.google.com): *Administrar → Acceso a la propiedad → Agregar* → mismo correo, rol **Lector**. Anota el **ID de propiedad** (número).

## 3. Cargar en GitHub (este repo → Settings → Secrets and variables → Actions)
| Tipo | Nombre | Valor |
|---|---|---|
| Secret | `GOOGLE_SA_JSON` | contenido completo del JSON descargado |
| Variable | `GSC_SITE` | `sc-domain:ubertransfer.cl` (o `https://ubertransfer.cl/` si la propiedad es de prefijo de URL) |
| Variable | `GA4_PROPERTY_ID` | ID numérico de la propiedad GA4 |
| Variable | `SITE_URL` | opcional; por defecto `https://ubertransfer.cl` |

Después borra el JSON descargado de tu equipo.

## 4. Primera corrida
Actions → *SEO y conversiones diario* → *Run workflow*. Si hay error 403, revisa el paso 2.

## 5. Monitoreo de caída (gratis)
UptimeRobot: monitores HTTP a `https://ubertransfer.cl/` y a la página de contacto, cada 5 min, aviso por correo. Confirma los límites vigentes del plan gratuito.

## 6. Cloudflare y Google Business Profile
Ver secciones 3 y 5 del plan (`docs/plan_ubertransfer_v2.html`). Google Ads: aprobar tope diario y medio de pago cuando se lance la campaña.

## Eventos GA4 que el sitio debe emitir
`click_whatsapp`, `click_phone`, `lead_submit` (y `booking_complete` si existe reserva online). Sin ellos, la alerta de conversiones dará falsos positivos: confírmalo antes de confiar en ella.
