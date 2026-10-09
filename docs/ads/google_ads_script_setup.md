# Google Ads Script de recomendaciones UberTransfer

Este módulo consulta Google Ads con `AdsApp.report()` y guarda recomendaciones en Firestore. Es solo lectura para Google Ads: no crea, edita, pausa ni publica campañas.

## Activación manual

1. En la cuenta de Google Ads de UberTransfer abre **Herramientas → Acciones masivas → Scripts**.
2. Crea un script nuevo y pega `tools/google_ads_scripts/ubertransfer_suggestions.gs`.
3. Revisa `FIRESTORE_PROJECT_ID` y deja `ubertransfer-ops`.
4. Autoriza el script cuando Google lo solicite. La autorización es para consultar AdsApp y escribir el documento `panel/aiSuggestions` en Firestore.
5. Ejecuta una vista previa. Debe terminar sin cambios en campañas.
6. Ejecuta `main()` y programa una frecuencia diaria si el resultado es correcto.

## Qué entrega

El panel lee `panel/aiSuggestions` y muestra propuestas con evidencia, fecha, campaña, motivo, confianza y confirmación pendiente. Si una consulta no devuelve filas, la tarjeta aparece como **DATOS INSUFICIENTES**; no se completan valores con estimaciones.

## Seguridad y límites

- No se usa una URL pública ni se exponen tokens en el panel.
- Firestore debe permitir que las cuentas autorizadas lean `panel/aiSuggestions`.
- El script nunca usa métodos de mutación de Google Ads.
- Si se revoca la autorización o falla una consulta, el panel conserva sus recomendaciones locales y muestra que la fuente de Apps Script no está disponible.
