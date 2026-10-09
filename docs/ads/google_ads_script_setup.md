# Google Ads Script de recomendaciones UberTransfer

Este módulo consulta Google Ads con `AdsApp.report()` y envía recomendaciones a un Web App de Apps Script. El Web App escribe `panel/aiSuggestions` en Firestore. Es solo lectura para Google Ads: no crea, edita, pausa ni publica campañas.

## Puente obligatorio

Google Ads Scripts no expone `ScriptApp.getOAuthToken()`. Por eso no se debe escribir Firestore directamente desde el script de Google Ads.

1. Crea un proyecto independiente en Google Apps Script y pega `tools/google_ads_scripts/ubertransfer_firestore_bridge.gs`.
2. En **Configuración del proyecto → Propiedades de la secuencia de comandos**, crea:
   - `BRIDGE_TOKEN`: una cadena aleatoria de al menos 32 caracteres.
   - `FIRESTORE_PROJECT_ID`: `ubertransfer-ops`.
3. Si el editor muestra `appsscript.json`, usa los permisos de `tools/google_ads_scripts/appsscript.json`.
4. Ejecuta una vez `autorizarPuente` desde el editor y acepta los permisos solicitados.
5. Implementa como **Aplicación web**, ejecutando como tú y con acceso **Cualquier usuario**. Copia la URL que termina en `/exec`.
6. En el script de Google Ads reemplaza `BRIDGE_URL` por esa URL y `BRIDGE_TOKEN` por el mismo token. No subas el token al repositorio.

## Activación manual

1. En la cuenta de Google Ads de UberTransfer abre **Herramientas → Acciones masivas → Scripts**.
2. Crea un script nuevo y pega `tools/google_ads_scripts/ubertransfer_suggestions.gs`.
3. Revisa `BRIDGE_URL`, `BRIDGE_TOKEN` y deja `LOOKBACK = 'LAST_30_DAYS'`.
4. Autoriza el script cuando Google lo solicite. La autorización es para consultar AdsApp y hacer una solicitud HTTPS al puente.
5. Ejecuta una vista previa. Debe terminar sin cambios en campañas.
6. Ejecuta `main()` y programa una frecuencia diaria si el resultado es correcto.

## Qué entrega

El panel lee `panel/aiSuggestions` y muestra propuestas con evidencia, fecha, campaña, motivo, confianza y confirmación pendiente. Si una consulta no devuelve filas, la tarjeta aparece como **DATOS INSUFICIENTES**; no se completan valores con estimaciones.

## Seguridad y límites

- La URL del puente es pública por diseño, pero exige un token aleatorio en el cuerpo y valida `id` y `ts`.
- No se usa `ScriptApp` dentro de Google Ads Scripts; esa API solo aparece en el Web App puente.
- Firestore debe permitir que las cuentas autorizadas lean `panel/aiSuggestions`.
- El script nunca usa métodos de mutación de Google Ads.
- Si se revoca la autorización o falla una consulta, el panel conserva sus recomendaciones locales y muestra que la fuente de Apps Script no está disponible.
