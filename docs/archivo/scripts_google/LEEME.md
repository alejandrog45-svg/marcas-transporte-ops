# Scripts de Google retirados (Google Ads + Bridge de Apps Script)

Retirados el **2026-10-09**. Ya no hacen falta: el workflow `panel-diario.yml` calcula las sugerencias
con `tools/panel/sync_suggestions_firestore.py` y las escribe en el **mismo** documento de Firestore
(`panel/aiSuggestions`) que escribía el Bridge. Este archivo explica qué eran y cómo volver a ponerlos.

**No hay secretos en este archivo ni en el repo.** El token del Bridge (`BRIDGE_TOKEN`) vivía en las
Propiedades del proyecto de Apps Script y, escrito en el código, en el script de Google Ads. Al archivar
las implementaciones del Bridge ese token dejó de servir. Si se reactiva, hay que generar uno nuevo.

## Cómo funcionaban

```
Google Ads (script "UberTransfer - Sugerencias Google Ads", cuenta 203-550-4421)
   │  consulta campañas y términos de búsqueda (AdsApp.report, solo lectura)
   │  arma sugerencias con reglas (buildSuggestions)
   ▼  POST JSON con el token
Bridge de Apps Script ("UberTransfer Firestore Bridge", Web App)
   │  valida el token y escribe en Firestore
   ▼
Firestore: proyecto ubertransfer-ops, documento panel/aiSuggestions
   ▼
Panel (menú Sugerencias → bloque de recomendaciones)
```

El script de Ads nunca tuvo horario (se ejecutaba a mano). El Bridge no tenía activadores.

## Respaldo del Bridge

En el Drive de `alejandrog45@gmail.com` hay un proyecto de Apps Script con el código completo y sin
implementaciones ni propiedades:

- Nombre: **RESPALDO - UberTransfer Firestore Bridge (retirado 2026-10-09)**
- URL: `https://script.google.com/home/projects/1prkJqRzxFdgwNaYU6k7uxcOwSeb8gODQjmKc6kpqGTihT3GTsEapPV_h/edit`

El proyecto original (`UberTransfer Firestore Bridge`, id `1vZU0-bY1sPIYNHNSVnmeGhBiKR_9ZBEcZLN1yjQtAtcIJWNa_KT1nNjj`)
sigue existiendo con su código, pero sus 3 implementaciones están archivadas.

### Reactivar el Bridge
1. Abrir el proyecto de respaldo (o el original) → ⚙ **Configuración del proyecto** → *Propiedades de la secuencia de comandos*.
2. Crear `BRIDGE_TOKEN` (aleatorio, mínimo 32 caracteres) y `FIRESTORE_PROJECT_ID` = `ubertransfer-ops`.
3. Ejecutar una vez `autorizarPuente` desde el editor y aceptar los permisos.
4. **Implementar → Nueva implementación → Aplicación web**: ejecutar como *Yo*, acceso *Cualquier usuario*.
5. Copiar la URL nueva de la Web App.

## Script de Google Ads

No quedó copia de su código en este repo (el navegador no permite extraerlo de forma segura). Si el
script sigue en la cuenta 203-550-4421 (*Herramientas → Acciones en bloque → Secuencias de comandos*),
copiar su código desde ahí antes de borrarlo. Para reconstruirlo, su lógica es:

- Consulta 1 (`campaigns`): `campaign.name`, `metrics.impressions`, `metrics.clicks`, `metrics.cost_micros`,
  `metrics.conversions`, `metrics.ctr` de `campaign` en `LAST_30_DAYS`.
- Consulta 2 (`terms`): `campaign.name`, `search_term_view.search_term` y las mismas métricas, de `search_term_view`.
- Con ellas arma 3 sugerencias (crear campaña basada en la actual, agregar el término con más clics, revisar
  términos costosos sin conversiones) y las envía por `UrlFetchApp.fetch` (POST JSON con el token) a la URL del Bridge.
- **Ojo con el nombre de las columnas:** `AdsApp.report` las devuelve como en la consulta
  (`metrics.cost_micros`, no `metrics.costMicros`). Ese error hacía que el costo saliera siempre 0
  y se corrigió el 2026-10-09.
- Los scripts de Google Ads no tienen `PropertiesService`: el token o la URL tendrían que ir en el código
  o en una hoja de cálculo privada.

La versión equivalente y mantenida está en Python: `tools/panel/sync_suggestions_firestore.py`.
