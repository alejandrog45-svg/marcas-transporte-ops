# Traspaso a la cuenta alejandrog45 (2026-10-04)

Este proyecto era `E:\ubertransfer-ops` (GitHub `oviedoem/ubertransfer-ops`, cuenta de la Ferretería). Se copió a `W:\PROYECTOS CUENTA ALEJANDROG45\marcas-transporte-ops` con repo nuevo y limpio, sin historial, bajo `alejandrog45-svg`.

## Qué cambió
- Carpeta, repo y paquete Python: `marcas-transporte-ops` / `marcas_transporte_ops` (`python -m marcas_transporte_ops {audit|seo}`).
- Bot de los workflows: `ops-bot`. User-Agent de auditoría y nombre del paquete del panel: sin "uber".
- Identidad git local: `alejandrog45-svg <alejandrog45@gmail.com>`. Sin remoto a `oviedoem`.
- Ejecuciones programadas (`schedule`) DESACTIVADAS en `audit-semanal`, `panel-diario` y `seo-diario`. Solo corren a mano (`workflow_dispatch`).

## Qué se dejó igual a propósito (cambiarlo rompe algo)
- `ubertransfer.cl` y `aereostar.cl`: son los sitios reales de Rafael que se auditan.
- Proyecto Firebase `ubertransfer-ops` (`.firebaserc`, `firebase.json`, workflow `panel-diario`): un ID de proyecto no se puede renombrar y el panel publicado vive en esa URL.
- Marcas en los textos del panel y en los datos (UberTransfer / Aereostar), claves internas `ubertransfer` del panel (guardadas en el navegador y en Firestore) y las negativas "conductor uber".
- Nombres de archivos de `docs/` y `consultas/` (el contenido de varios se cita entre sí).

## Qué falta para el traspaso completo (lo hace una persona)
1. Crear en el repo nuevo los secretos `FIREBASE_SERVICE_ACCOUNT` y `GOOGLE_SA_JSON` (no se pueden copiar; la cuenta de servicio `panel-deployer` se reutiliza o se recrea).
2. Antes de reactivar los `schedule`, **desactivar los del repo viejo** de `oviedoem` (si no, dos repos publican al mismo Firebase).
3. Clave del panel: archivo `E:\config\ubertransfer_panel_key.dpapi` (cifrado DPAPI) y documento Firestore `panel/clave`. `tools/panel/build.py` la lee de esa ruta. No va al repo ni a `W:`.
4. Firebase CLI: la cuenta por defecto del equipo es la de la Ferretería. Usar siempre `--account alejandrog45@gmail.com`; nunca `firebase login:use`.
5. Push: usar el `gh` aislado de `W:\PROYECTOS CUENTA ALEJANDROG45\herramientas-portables\gh.cmd` (cuenta `alejandrog45-svg`), no el administrador de credenciales de Git.
