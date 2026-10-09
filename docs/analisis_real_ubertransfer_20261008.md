# Análisis de mejoras para el panel UberTransfer

## Alcance

Se compararon:

- `docs/ads/campana_amadigital_analisis.html` como referencia histórica, no como datos propios.
- `docs/plan_ubertransfer_v2.html` como plan y auditoría del sitio.
- `data/google_ads_ubertransfer.json` como extracción real de solo lectura de Google Ads.
- `tools/panel/sync_google_ads.py`, `tools/panel/build.py` y `tools/panel/template.html` como implementación actual.

## Datos reales disponibles

Última extracción: **8 de octubre de 2026, hora de Chile**. Cuenta Google Ads `203-550-4421`; campaña `24325669851`, llamada `Campaign #1`.

| Métrica | Valor real |
|---|---:|
| Campañas | 1 |
| Impresiones | 794 |
| Clics | 52 |
| CTR calculado | 6,55 % |
| Costo | $15.068 CLP |
| CPC calculado | $290 CLP |
| Conversiones registradas por Google Ads | 0 |
| Términos de búsqueda | 193 |
| Franjas horarias | 14 |
| Dispositivos | 3 |
| Registros geográficos | 2 |

Hallazgos de esta muestra:

- El 86,5 % de los clics provino de móvil; conviene priorizar revisión móvil de la landing y del botón de WhatsApp.
- Las franjas con más clics fueron 08:00, 09:00, 12:00 y 19:00, con 7 clics cada una. Esto es una señal inicial, no una regla de puja: solo hay un día.
- Google entregó solo dos tipos geográficos: `AREA_OF_INTEREST` y `LOCATION_OF_PRESENCE`, ambos con criterio país Chile. Aún no hay comunas o regiones reales para mostrar.
- Los términos con clics incluyen búsquedas de competidores (`cabify aeropuerto`, `transvip reserva`) y términos de transporte al aeropuerto. Deben clasificarse para decidir negativas y grupos, pero no deben convertirse automáticamente en cambios de campaña.
- No hay conversiones en Google Ads. Por tanto, el panel no puede afirmar cuántos usuarios reservaron, escribieron por WhatsApp o llamaron.

## Mejoras recomendadas para el panel

### Prioridad alta

1. Mostrar CTR y CPC reales calculados junto a impresiones, clics, costo y conversiones.
2. Mostrar explícitamente **0 conversiones registradas** y diferenciarlo de “dato faltante”.
3. Quitar la etiqueta global `SIMULACIÓN` del panel de UberTransfer. Debe decir `DATOS REALES · SOLO LECTURA`; los datos del Planificador deben quedar etiquetados aparte como referencia histórica.
4. Mostrar siempre fecha, zona horaria, período consultado y hora de última sincronización.
5. Mantener visible la alerta de cambio de nombre de campaña/anuncio, sin editar nada automáticamente.

### Prioridad media

1. Añadir un resumen de términos: marca, competidor, aeropuerto, transporte general y posible negativa. La clasificación debe rotularse como automática y revisable.
2. Añadir costo por clic y CTR por dispositivo y por franja horaria.
3. Cambiar “regiones” por “distribución geográfica disponible” hasta que Google Ads entregue ciudad/comuna/región.
4. Ampliar la consulta de Google Ads a `user_location_view`/criterios geográficos para obtener detalle territorial cuando la cuenta lo permita.
5. Conservar un histórico diario de al menos 90 días y mostrar días sin datos como ausencia, no como cero inventado.

### Bloqueo de medición de resultados

Para medir contactos y reservas se necesita una fuente real adicional:

- eventos GA4/GTM para WhatsApp, teléfono y formulario;
- una conversión de Google Ads para cada acción;
- idealmente `gclid` y conversiones offline cuando exista una reserva confirmada.

Hasta que eso esté conectado, el panel debe mostrar “conversiones no registradas” y no estimar clientes.

## Herramientas de costo cero revisadas

### Ya disponibles y recomendadas

- **GitHub Actions:** extracción diaria, validación, armado y publicación; ya está funcionando en `.github/workflows/panel-diario.yml`.
- **Firebase Hosting Spark:** publicación estática del panel; ya está funcionando.
- **Cloud Firestore:** preferencias e histórico pequeño dentro de la cuota gratuita; actualmente las reglas limitan el acceso a las cuentas autorizadas.
- **Google Ads API de solo lectura:** fuente real de campaña, términos, horarios, dispositivos y geografía disponible.

### No incorporar todavía

- **Cloud Functions/Firebase Extensions:** requieren asociar facturación y pasar a Blaze; no cumplen la condición estricta de costo cero del proyecto.
- **Acciones de correo de terceros de GitHub Marketplace:** requieren SMTP y secretos adicionales; no son necesarias para mejorar el panel y agregan dependencia externa.
- Repositorios públicos no relacionados: no copiar código sin revisar licencia, seguridad y mantenimiento.

Firebase confirma que Hosting y Firestore tienen uso sin costo, pero Cloud Functions requiere cuenta de facturación y puede actualizar el proyecto a Blaze. [Planes de Firebase](https://firebase.google.com/docs/projects/billing/firebase-pricing-plans)

## Conclusión

El panel ya tiene la base correcta: sincronización diaria de Google Ads, histórico, términos, franjas, dispositivos, regiones disponibles y alertas de cambios. La mejora inmediata más útil es limpiar la presentación para separar datos reales de referencias, añadir CTR/CPC y declarar la ausencia de conversiones. La siguiente mejora técnica debe ser el detalle geográfico y la medición de conversiones; ninguna de las dos debe simularse.

## Tarea final pendiente: acceso al panel

La última comprobación debe investigar el error visible `auth/internal-error` al iniciar sesión en `ubertransfer-ops.firebaseapp.com`. Posibles puntos a verificar, sin cambiar reglas ni credenciales durante esta revisión:

1. Dominios autorizados de Firebase Authentication y OAuth.
2. Que el correo utilizado esté en la lista permitida de `firestore.rules`.
3. Sesión/cookies de Google y bloqueo de ventanas emergentes del navegador.
4. Que la aplicación publicada y `authDomain` correspondan al mismo proyecto Firebase.
5. Consola del navegador y registros de Authentication para obtener el error exacto.
