# PROMPT PARA CLAUDE CODE (app del PC) — Proyecto UberTransfer.cl

> Pega TODO este archivo como primer mensaje en Claude Code, abierto en la unidad `E:\`.
> Requisito previo: haber iniciado sesión en GitHub con la cuenta `oviedoem` en el navegador.

---

## 0. Contexto (léelo entero antes de actuar)

Trabajas para el dueño de **UberTransfer.cl** (traslados aeropuerto Santiago, turismo, corporativo, compartidos). El sitio es **WordPress + Divi + Rank Math + LiteSpeed**; **no se migra**.
Ya existe el repo privado **`oviedoem/ubertransfer-ops`** (rama `main`) con: auditoría técnica del sitio, extracción de Search Console y GA4, reglas de alerta, tests, 3 workflows de GitHub Actions, el plan (`docs/plan_ubertransfer_v2.html`) y el conocimiento del negocio (`conocimiento/`). Solo hace falta traerlo al disco y operarlo desde aquí.

Objetivo del proyecto: **más reservas por peso invertido** (SEO + Google Ads controlado), con la mínima intervención manual y costo de infraestructura cercano a $0. Nadie puede garantizar el puesto #1 en Google: no lo prometas ni lo uses como métrica.

## 1. Reglas inviolables

1. **Proyecto aislado.** UberTransfer NO se mezcla con FerreSystem ni con ningún otro proyecto de `E:\`. No leas, edites ni ejecutes nada dentro de `E:\ferresystem`, `E:\ferreteria-oviedo` u otros proyectos, salvo el **inventario de solo lectura** del paso 3.
2. **Cero secretos en archivos, chats ni commits.** La clave de Google va solo como *Secret* de GitHub. Nunca la imprimas, la pegues en un chat de IA ni la guardes en el repo. Si ves una credencial, avisa y detente.
3. **Detectas y propones; una persona aprueba.** Nunca cambies presupuestos, pujas, anuncios, ni publiques contenido/cambios en el sitio sin mi confirmación explícita en esta conversación.
4. **Pagos, contraseñas, códigos 2FA, CAPTCHA, verificaciones de identidad: los hago yo.** Te detienes y me avisas exactamente qué hacer. No intentes eludirlos.
5. **Sin invenciones.** Horarios, rutas, comunas, tarifas y flota son datos pendientes hasta que yo los confirme. Márcalos `PENDIENTE`.
6. **Antes de cada cambio de código**, declara: `TOCO / ARCHIVO / RAZÓN / NO TOCO`. Cambio mínimo. Corre `python -m pytest -q` antes de commitear.
7. **Regla antirretroceso:** no reviertas decisiones registradas en `conocimiento/` ni en el `CLAUDE.md` del proyecto sin que yo lo pida.
8. **Ahorro de tokens:** no releas archivos ya leídos, no abras archivos innecesarios, respuestas cortas y con resultados verificados. Activa la skill `ahorro-tokens` si existe.
9. **Al cerrar cada sesión (obligatorio):** actualiza `CLAUDE.md` (historial) y la carpeta `conocimiento/` del proyecto, commitea y sube.

## 2. Paso 1 — Crear la carpeta en `E:\` y traer el repo

Git portable: `E:\git-portable\mingw64\bin\git.exe`. Usa PowerShell.

```powershell
$git = "E:\git-portable\mingw64\bin\git.exe"
if (Test-Path "E:\ubertransfer-ops") { "YA EXISTE: no borrar, revisar" ; Get-ChildItem "E:\ubertransfer-ops" -Force | Select-Object -First 20 }
else { & $git clone https://github.com/oviedoem/ubertransfer-ops "E:\ubertransfer-ops" }
& $git -C "E:\ubertransfer-ops" log --oneline -3
& $git -C "E:\ubertransfer-ops" status -sb
```

- Si la carpeta ya existía y no está vacía, **no la borres ni la sobrescribas**: muéstrame qué contiene y pregúntame.
- Si el clon pide autenticación, avísame; yo inicio sesión (no me pidas ni guardes tokens en texto).
- Configura identidad solo en este repo: `git config user.name` / `user.email` con los datos que yo te indique.
- Trabaja siempre desde `E:\ubertransfer-ops`. Lee su `CLAUDE.md` y `conocimiento\conocimiento_negocio.md`.

## 3. Paso 2 — Inventario de herramientas portables (solo lectura)

Quiero aprovechar lo que ya tengo instalado sin instalar nada nuevo. Haz un **inventario de solo lectura** y muéstrame una tabla `herramienta | ruta | versión | ¿sirve para UberTransfer? (sí/no y por qué)`:

```powershell
Get-ChildItem "E:\" -Directory -Force | Select-Object Name, LastWriteTime
Get-ChildItem "E:\" -Directory -Recurse -Depth 2 -Include *portable* -ErrorAction SilentlyContinue | Select-Object -First 40 FullName
foreach ($c in "python","py","node","npm","gh","firebase","git") { $x = Get-Command $c -ErrorAction SilentlyContinue; "$c -> $($x.Source)" }
```

Reglas del inventario: no abras contenidos de otros proyectos, no ejecutes programas desconocidos, no copies credenciales. Solo nombres, rutas y versiones (`--version`). Si falta Python 3.11+, dime cómo obtener una versión portable; no instales sin mi OK.

Luego prepara el entorno **dentro del repo**: `python -m venv .venv` (el `.venv` ya está en `.gitignore`), `pip install -r requirements-dev.txt`, `python -m pytest -q` (debe dar 9 passed) y `python -m ubertransfer_ops audit` con `PYTHONPATH=src`. Reporta el resultado.

## 4. Paso 3 — Extensión de Chrome (Claude in Chrome) para las tareas web

Usa la extensión de Chrome para hacer, **guiado y paso a paso**, las configuraciones web que requieren mi sesión. Yo inicio sesión; tú navegas y rellenas solo campos no sensibles. Pídeme confirmación antes de cada clic que guarde, active, pague o publique.

Tareas, en este orden (detalle en `docs\setup_accesos.md`):

1. **Google Cloud** → proyecto `ubertransfer-ops` → habilitar *Search Console API* y *Google Analytics Data API* → crear cuenta de servicio `ubertransfer-reader` (sin roles) → generar clave JSON. **La clave la descargo yo y la pego yo directamente en el Secret de GitHub.** Tú no la lees ni la muestras.
2. **Search Console** → propiedad de `ubertransfer.cl` → agregar el correo de la cuenta de servicio con permiso *Restringido*.
3. **GA4** → agregar el mismo correo como *Lector* → anotar el ID numérico de propiedad. Verificar en *Informes en tiempo real* que se emiten `click_whatsapp`, `click_phone`, `lead_submit`; si faltan, lista qué etiquetas crear en GTM (GTM-WLPJJD4J) **sin publicarlas** hasta que yo apruebe. Comprueba también que GTM y el `gtag` directo (G-26K0MDTFY1) no cuenten doble.
4. **GitHub** (`oviedoem/ubertransfer-ops` → Settings → Secrets and variables → Actions): Secret `GOOGLE_SA_JSON`; variables `GSC_SITE` (`sc-domain:ubertransfer.cl` o prefijo de URL según la propiedad), `GA4_PROPERTY_ID`, `SITE_URL`. Luego ejecutar el workflow *SEO y conversiones diario* con *Run workflow* y revisar el resultado.
5. **Google Business Profile**: revisar el estado de la ficha, horario real (hoy el schema del sitio dice 09:00–17:00 pero el texto dice 24/7: **PENDIENTE de decisión mía**), teléfono, área de servicio. La verificación la hago yo.
6. **Cloudflare (plan gratis)**: solo preparar la lista de cambios (nameservers, bloqueo de `xmlrpc.php`, caché). No cambies nameservers sin mi OK explícito, porque puede tumbar el sitio.
7. **UptimeRobot (gratis)**: monitores HTTP a `https://ubertransfer.cl/` y a la página de contacto, cada 5 min, aviso por correo. Confirma los límites vigentes del plan.
8. **Google Ads** (solo lectura al inicio): revisar la cuenta y conversiones importadas. **No crear ni activar campañas** hasta que yo apruebe tope diario y método de pago.

## 5. Paso 4 — ChatGPT, Gemini y Meta AI como apoyo (desde Chrome)

Mis suscripciones (ChatGPT, Gemini Plus, Meta AI) son de uso en chat. **No dan acceso por API**, así que solo se usan a través del navegador, con estas reglas:

| Herramienta | Úsala para | Nunca |
|---|---|---|
| **Gemini** | Ideas de imágenes, revisión de textos de ficha Business, apoyo con Looker Studio | Pegar claves, datos de clientes |
| **ChatGPT** | Segunda opinión sobre el plan, borradores de textos (ES/EN) de landings | Aceptar cifras o datos del negocio sin que yo los confirme |
| **Meta AI** | Solo si más adelante hay Instagram/Meta Ads | Nada por ahora |

Flujo: tú redactas un prompt breve **sin datos sensibles**, lo envías en la pestaña de la herramienta, traes la respuesta, la **contrastas** con los datos verificados del proyecto y me presentas el resultado con diferencias. Todo texto que vaya al sitio pasa por mí antes de publicarse. Cita si una cifra o afirmación viene de una IA externa.

## 6. Paso 5 — Tareas automáticas

Lo que ya corre solo en GitHub Actions (sin tu PC): auditoría semanal, SEO/conversiones diario, CI, y un **Issue** automático si hay alertas. En el PC solo automatiza lo que aporte:

- **Rutina diaria (propón, no actives sin mi OK):** una tarea programada de Windows (Task Scheduler) o el skill `loop` que, con el PC encendido, haga `git pull`, lea `reports\seo_latest.md` y `reports\audit_latest.md`, y me resuma en 5 líneas: alertas, 3 oportunidades SEO (posición 8–20) y 1 acción recomendada. Solo lectura; no commitea ni publica.
- **Semanal:** revisar términos de búsqueda de Google Ads (por el conector/MCP de Ads de solo lectura o la interfaz) y proponer negativas. Yo apruebo.
- Cada automatización nueva: primero descríbemela (qué hace, con qué cuenta, qué puede romper) y espera mi OK.

## 7. Paso 6 — Trabajo de contenido (cuando yo confirme los datos)

Datos PENDIENTES que debo darte antes de construir páginas: horario real, comunas y rutas atendidas, tarifas, flota, condiciones (pago, cambio de vuelo). Cuando los tenga, propón en `docs\` (no en el sitio):

- Página **Tarifas** dedicada (hoy `/tarifas/` da 404; el menú apunta a `/#tarifas`).
- Páginas de ruta (aeropuerto → comuna clave) y versión **EN** con `hreflang`.
- Reescritura de `title` (≤ ~60 car.) y `description` (≤ ~155 car.): hoy hay titles de 74–92 car. y una description de 181 en `/servicio-…`.
- `lazy-load` en imágenes (39 en la home) y schema `LocalBusiness` con teléfono y `areaServed`.
- Campaña Search en **borrador**: estructura, keywords (validadas con Keyword Planner), negativas, anuncios. Sin activar.

Todo como borrador en el repo; yo apruebo qué se publica y cómo (WordPress lo edito yo o me guías paso a paso).

## 8. Definición de terminado (esta primera sesión)

- [ ] `E:\ubertransfer-ops` existe, con el repo clonado y tests en verde.
- [ ] Inventario de herramientas portables entregado y aprobado por mí.
- [ ] Accesos de Google y secretos de GitHub configurados; el workflow *SEO y conversiones diario* corrió sin error (o el error está diagnosticado).
- [ ] UptimeRobot configurado.
- [ ] Lista de datos PENDIENTES enviada a mí.
- [ ] `CLAUDE.md` y `conocimiento\` actualizados, commit y `git push` a `main` de `oviedoem/ubertransfer-ops`.

Empieza por el **Paso 1** y avísame en cada punto donde necesites que yo actúe.
