# Accesos para trabajar desde la nube (sesiones de Claude Code en la nube)

Actualizado 2026-10-10. Sin claves ni contraseñas: aquí solo se dice QUÉ hay y QUÉ falta. Una tarea a la vez, solo lectura en Google Ads.

| Acceso | Estado | Cómo se usa / qué falta |
|---|---|---|
| GitHub (`alejandrog45-svg`, 3 repos) | OK | Herramientas MCP de GitHub; rama de la sesión → PR en borrador |
| Publicar el panel | OK (solo con «sí, publica») | push a `main` + flujo manual `panel-diario.yml` (Secrets: `FIREBASE_SERVICE_ACCOUNT`, `GEMINI_API_KEY`, `PANEL_DATA_KEY`, Ads) |
| Google Ads UberTransfer (`203-550-4421`) | OK por API en el flujo diario; lectura por Supermetrics si el dueño la autoriza en la sesión | La autorización de Supermetrics NO se guarda en el repo: se repite cada sesión |
| Google Ads Aereostar (`548-530-8262`) | Lectura por Supermetrics OK | Falta confirmar que las credenciales del repo la leen: lanzar `ads-acceso-aereostar.yml` (solo está disponible tras fusionar a `main`) |
| Search Console `ubertransfer.cl` | SIN permiso | Verificar la propiedad (Rafael) |
| GA4 `G-26K0MDTFY1` | SIN acceso | Rafael debe dar acceso; hoy solo se ve otra propiedad ajena al proyecto |
| Navegador | SIN Chrome del dueño | Solo Chromium sin sesiones (`/opt/pw-browsers`). El plugin «Browser Use» debe estar HABILITADO en claude.ai y la sesión debe ser NUEVA |
| Firebase CLI / clave del panel local | NO está en la nube | Reglas de Firestore y armado con clave: en el PC |

Reglas: nunca contraseñas ni 2FA; Google lo inicia el dueño; sin cambios en presupuesto/pujas/anuncios; sin publicar sin aprobación. Permisos preaprobados de solo lectura en `.claude/settings.json` (pruebas, estado de git); `firebase deploy`, `firebase login` y el push forzado están bloqueados.
