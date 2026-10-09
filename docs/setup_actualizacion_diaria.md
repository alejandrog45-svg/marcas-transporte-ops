# Actualización diaria del panel (GitHub Actions + Firebase Hosting)

Cada día a las 11:45 UTC (07:45–08:45 hora de Chile) GitHub:
1. audita ubertransfer.cl (datos reales del día),
2. sincroniza Google Ads en modo solo lectura,
3. genera y guarda las sugerencias en Firestore (`panel/aiSuggestions`),
4. arma el panel (`python tools/panel/build.py`),
5. guarda la auditoría en `data/` (histórico),
6. publica el panel en https://ubertransfer-ops.web.app.

Las sugerencias se calculan con reglas transparentes sobre los datos reales; no
son una IA generativa y no crean ni modifican campañas. El script de Google
Ads/Apps Script queda disponible como alternativa manual, pero ya no es
necesario ejecutarlo para la actualización diaria.

Sin la clave de Firebase (paso 1–3) el flujo igual audita y guarda el histórico, pero **avisa y no publica**.

## Lo que haces tú (una sola vez, ~10 minutos)
Usa la cuenta de Google `alejandrog45@gmail.com` para Google Cloud y la cuenta de GitHub `oviedoem` para GitHub.

### 1. Crear la cuenta de servicio con permiso mínimo
1. https://console.cloud.google.com/iam-admin/serviceaccounts/create?project=ubertransfer-ops
2. Nombre: `panel-deployer` → **Crear y continuar**.
3. En "Rol", agrega estos dos y pulsa **Continuar** → **Listo**:
   - **Firebase Hosting Admin**
   - **API Keys Viewer**
   - **Cloud Datastore User** (para guardar `panel/aiSuggestions` en Firestore)
   (Solo pueden publicar el sitio de este proyecto. Sin acceso a facturación ni a otros servicios.)

### 2. Crear la clave (JSON)
1. https://console.cloud.google.com/iam-admin/serviceaccounts?project=ubertransfer-ops → abre `panel-deployer`.
2. Pestaña **Claves** → **Agregar clave** → **Crear clave nueva** → **JSON** → **Crear**. Se descarga un archivo.

### 3. Guardarla como secreto en GitHub
1. https://github.com/oviedoem/ubertransfer-ops/settings/secrets/actions/new
2. Nombre: `FIREBASE_SERVICE_ACCOUNT`
3. Valor: abre el JSON con el Bloc de notas → Ctrl+A → Ctrl+C → pégalo en el cuadro → **Add secret**.
4. **Borra el archivo JSON descargado** (y vacía la papelera). No lo pegues en chats ni lo subas a ningún lado.

### 4. Probar
1. https://github.com/oviedoem/ubertransfer-ops/actions/workflows/panel-diario.yml → **Run workflow** → **Run workflow**.
2. Debe terminar en verde en ~2–3 minutos. Después, en el panel, pulsa **Consultar en vivo**: "La versión que ves es la publicada" debe salir OK y la hora de la auditoría debe ser de hoy.

## Si falla
- Error de permisos (`403`, `serviceusage`): agrega el rol **Service Usage Consumer** a `panel-deployer` en https://console.cloud.google.com/iam-admin/iam?project=ubertransfer-ops
- "Falta el secreto FIREBASE_SERVICE_ACCOUNT": revisa el nombre exacto del secreto (paso 3).
- GitHub te avisa por correo si una corrida programada falla.

## Seguridad
- La clave solo vive como secreto de GitHub (cifrado). El flujo la escribe en un archivo temporal de la máquina de GitHub y la borra al terminar.
- Para rotarla: crea otra clave (paso 2), reemplaza el secreto y borra la clave antigua en la consola.
- Lo que sigue **sin** actualizarse solo: frases y previsión de Google (manual) y Search Console/GA4 (falta el acceso del dueño del sitio).
