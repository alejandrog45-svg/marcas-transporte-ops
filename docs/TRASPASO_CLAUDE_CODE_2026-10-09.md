# Traspaso a Claude Code — UberTransfer

Fecha: 2026-10-09 (America/Santiago)

## Punto exacto de partida

- Carpeta local: `W:\PROYECTOS CUENTA ALEJANDROG45\marcas-transporte-ops`
- Rama: `main`
- Remoto Git: `https://github.com/alejandrog45-svg/marcas-transporte-ops.git`
- Último commit: `25f183a style: aplicar identidad UberTransfer a todos los menus`
- Firebase project: `ubertransfer-ops`
- Hosting publicado: `https://ubertransfer-ops.web.app`
- URL preferida para probar el login: `https://ubertransfer-ops.firebaseapp.com/`
- El despliegue directo de Hosting terminó correctamente después del último commit.

## Qué se hizo en esta sesión

1. Se conectó la actualización diaria de Google Ads al workflow:
   - `.github/workflows/panel-diario.yml`
   - horario: `11:45 UTC` (aprox. `08:45` Santiago en horario de verano).
2. Después de sincronizar Google Ads, el workflow genera sugerencias de solo lectura y las guarda en Firestore en `panel/aiSuggestions`.
3. Las sugerencias usan la campaña activa (`ENABLED`/`ACTIVE`) y el histórico acumulado; si no hay campaña activa, usan la mejor fila disponible sin inventar datos.
4. La publicación continúa aunque Firestore no tenga permiso; en ese caso deja una advertencia y el panel se publica con los datos locales.
5. El panel calcula recomendaciones transparentes: campaña actual, términos, costos sin conversiones e historial. No crea campañas, no modifica pujas ni presupuestos.
6. Se rediseñaron todos los menús y botones de navegación con identidad UberTransfer: rojo `#ed1c24`, rojo oscuro para hover, fondo blanco, negro de contraste y verde como acento.
7. La fuente del diseño es `tools/panel/template.html`. `site/index.html` es generado y está ignorado por Git.

## Arquitectura y conexiones

- Fuente de Google Ads: `tools/panel/sync_google_ads.py`.
- Archivo sincronizado: `data/google_ads_ubertransfer.json`.
- Sugerencias del workflow: `tools/panel/sync_suggestions_firestore.py`.
- Firestore: proyecto `ubertransfer-ops`, documento `panel/aiSuggestions`.
- Panel web: `tools/panel/template.html` → `python tools/panel/build.py` → `site/index.html`.
- Hosting: `firebase.json`, sitio estático `site/`.
- Login del panel: Firebase Auth; no cambiar `authDomain` sin revisar la URI `firebaseapp.com`.
- Datos privados/cifrados: `data/panel_data.enc.json`, clave local protegida en `E:\config\ubertransfer_panel_key.dpapi`. No copiar ni mostrar claves.
- Apps Script de Google Ads queda como fuente alternativa/manual; el workflow diario principal ya no depende de ejecutarlo.
- Secretos de Actions esperados: `GOOGLE_ADS_OAUTH_CLIENT_ID`, `GOOGLE_ADS_OAUTH_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `FIREBASE_SERVICE_ACCOUNT`.

## Pendiente crítico

### Firebase CLI local

La CLI estaba autenticada como `ferreteriaoviedo.elmanzano@gmail.com` al comenzar. Para desplegar el cambio se autenticó temporalmente como `alejandrog45@gmail.com`. Después se cerraron ambas sesiones; actualmente `firebase login:list` indica que no hay cuentas autorizadas.

Google está solicitando la contraseña de `ferreteriaoviedo.elmanzano@gmail.com` para restaurar la cuenta local. Claude Code debe:

1. completar el login solo si el dueño introduce la contraseña en la pantalla de Google;
2. verificar con `E:\npm-global\firebase.cmd login:list` que quede Ferretería;
3. no usar `firebase login:use`, porque cambia la cuenta global y puede afectar otros proyectos;
4. para futuros despliegues de este proyecto, preferir una cuenta explícita o una sesión temporal y devolver siempre la CLI a Ferretería.

El estado de autenticación de la CLI no afecta al Hosting ya publicado ni al workflow de GitHub.

### Permiso Firestore del workflow

La cuenta de servicio del secreto `FIREBASE_SERVICE_ACCOUNT` debe tener `Cloud Datastore User`, además de los permisos de Hosting documentados en `docs/setup_actualizacion_diaria.md`. Si falta, el workflow advertirá y seguirá publicando, pero `panel/aiSuggestions` no se actualizará.

## Cómo continuar sin romper el estado

```powershell
Set-Location 'W:\PROYECTOS CUENTA ALEJANDROG45\marcas-transporte-ops'
git status --short
git pull --rebase origin main
python tools/panel/build.py
python -m pytest -q
python tools/check_seguridad.py
```

Para cambios de diseño:

1. Editar solo `tools/panel/template.html` y/o `tools/panel/extra.css`.
2. Regenerar con `python tools/panel/build.py`.
3. Probar `https://ubertransfer-ops.firebaseapp.com/` en PC y móvil.
4. Hacer commit y push a `main`.
5. Desplegar solo Hosting, nunca Firestore, salvo que cambien reglas:

```powershell
& 'E:\npm-global\firebase.cmd' deploy --only hosting --project ubertransfer-ops --non-interactive
```

No editar manualmente `site/index.html`, `site/aereostar/index.html`, `docs/panel_keywords.html` ni `docs/panel_aereostar.html`: son salidas generadas.

## Archivos locales no pertenecientes al cambio

No borrar ni commitear sin confirmación:

- `439447485_1125132095485641_6249746465832022138_n.jpg` — logo entregado por el dueño, actualmente sin seguimiento.
- `docs/archivo/panel_keywordsCOPIANOUSAR.html` — archivo local preexistente sin seguimiento.

## Regla de trabajo

Antes de cada cambio, declarar internamente: `TOCO / ARCHIVO / RAZÓN / NO TOCO`. Mantener el sistema en modo lectura para Google Ads. No activar campañas, no modificar presupuestos y no publicar cambios del sitio real sin aprobación explícita.
