# Auditoría completa — UberTransfer Ops

Fecha de revisión: 30 de septiembre de 2026, hora de Chile.

## Alcance y evidencia

Se revisaron:

- Repositorio GitHub `oviedoem/ubertransfer-ops`, rama `main`.
- Panel publicado en `https://ubertransfer-ops.firebaseapp.com/`.
- Interacción real con Guía, Palabras clave, Simulador y Datos y verificación.
- Código de auditoría, extracción Google, armado del panel, workflows y pruebas.
- Datos versionados del repositorio: 170 filas de keywords, previsión de Google, Trends y auditoría técnica.
- Documentación oficial de Google Analytics Data API, Google Ads, web.dev y Firebase Hosting.

No se accedió a Search Console ni GA4 porque el propio panel confirma que todavía están sin conectar. Por lo tanto, no presento tráfico, conversiones ni rendimiento SEO como hechos.

## Veredicto ejecutivo

El panel tiene una base sólida para investigación y simulación sin gasto. Está bien encaminado en trazabilidad: muestra fecha de origen, huella SHA-256, fuente, advertencias y una verificación interna de 17/17 controles correctos.

No lo considero todavía un sistema de medición operativo completo. Las prioridades son:

1. Proteger el panel si contiene información interna.
2. Corregir la medición de sesiones GA4 antes de conectar automatizaciones.
3. Hacer que una auditoría sin páginas sea un error explícito.
4. Separar visualmente dato confirmado, dato observado en el sitio, estimación de Google y supuesto del usuario.
5. Evitar que el simulador sugiera crecimiento lineal de clics por encima de la previsión oficial.

## Hallazgos confirmados

### 1. El panel está públicamente accesible — prioridad P0 si debe ser interno

El sitio carga sin autenticación. El HTML contiene `noindex, nofollow`, y `firebase.json` añade `X-Robots-Tag: noindex, nofollow`, pero eso solo reduce indexación; no impide que cualquier persona con el enlace vea el panel.

El propio panel lo reconoce en “Datos y verificación”. Esto es correcto como advertencia, pero insuficiente como protección.

Riesgo concreto: quedan expuestos keywords, pujas, previsiones, notas internas y recomendaciones de campaña.

Recomendación: antes de agregar datos de campañas reales, implementar autenticación real. Si el panel seguirá siendo deliberadamente público, quitar o separar la información interna y mantenerlo como demostrador público.

### 2. La auditoría SEO puede ocultar un fallo de descubrimiento — prioridad P0

En `src/ubertransfer_ops/audit.py`, `collect_urls()` atrapa errores de red/XML y devuelve una lista vacía. `run()` puede producir `pages: []` y finalizar sin una alerta de “auditoría no ejecutada”.

Eso puede generar un informe aparentemente exitoso cuando robots.txt, el sitemap o el servidor fallan.

Recomendación mínima:

- Fallar si no se descubre ninguna URL.
- Registrar por separado el estado de robots.txt, sitemap índice y sitemaps hijos.
- Añadir una prueba que confirme que sitemap inaccesible o vacío genera alerta.

### 3. La extracción GA4 usa el conteo de eventos como sustituto de sesiones — prioridad P0 antes de conectar GA4

En `src/ubertransfer_ops/google_api.py`, `ga4_events()` consulta la métrica `eventCount` por `eventName` y luego calcula:

```python
"sessions": counts.get("session_start", 0)
```

El código está contando ocurrencias del evento `session_start`, no solicitando la métrica `sessions`. Aunque ambos conceptos se relacionan, no deben presentarse como idénticos sin una validación explícita.

La documentación oficial de Google define `sessions` como una métrica propia: el número de sesiones iniciadas en el sitio o app. Debe consultarse como métrica `sessions` en el reporte, idealmente en una segunda consulta o junto con `eventCount`.

Recomendación: cambiar el reporte para solicitar `sessions` y `eventCount`; conservar ambos campos y usar `sessions` para las alertas.

### 4. El simulador funciona, pero extrapola linealmente fuera de la previsión oficial

Prueba realizada en el panel:

- Presupuesto: 10.000 CLP diarios.
- 31 días.
- Resultado del cálculo: 2.356 clics mensuales.
- Previsión oficial visible de Google para 10 frases: aproximadamente 1.100 clics con aproximadamente 4.600 CLP diarios.

El panel sí muestra una advertencia indicando que probablemente no habrá más clics si el tráfico disponible está limitado. Aun así, la cifra lineal aparece como resultado principal y puede ser interpretada como previsión.

Recomendación: separar dos resultados:

- “Cálculo matemático por presupuesto/CPC”, sin llamarlo previsión.
- “Rango limitado por previsión de Google”, cuando exista una previsión compatible.

Opción prudente: no permitir que el escenario comparable con Google supere automáticamente los clics oficiales sin mostrar una etiqueta fuerte de “extrapolación no validada”.

### 5. La verificación 17/17 mide consistencia interna, no exactitud comercial

El panel lo declara correctamente, pero conviene reforzarlo visualmente. Los controles prueban, entre otras cosas, que:

- Hay 170 filas en el panel y 170 en el archivo.
- La huella coincide.
- No hay frases repetidas.
- Las pujas baja/alta son coherentes.
- La previsión de Google cuadra aproximadamente con CPC, CTR, impresiones y presupuesto.

Eso no confirma que las keywords sean adecuadas, que las pujas sigan vigentes, que el sitio convierta, ni que el negocio atienda todas las rutas mostradas.

Recomendación: dividir el resumen en tres bloques: “integridad del archivo”, “coherencia matemática” y “validación de negocio pendiente”.

### 6. Search Console y GA4 siguen sin conectar; el workflow SEO puede omitir trabajo sin error

`cli.py` imprime que el job SEO se omite si faltan credenciales y devuelve código 0. Esto evita un fallo técnico, pero puede dar una falsa sensación de automatización activa.

Recomendación:

- Crear una alerta visible en GitHub Actions cuando falten `GOOGLE_SA_JSON`, `GSC_SITE` o `GA4_PROPERTY_ID`.
- Mostrar en el panel la fecha del último reporte real de Search Console/GA4 o “sin ejecutar”.
- No presentar el job como “SEO diario” operativo mientras las fuentes sigan desconectadas.

### 7. Los workflows tienen permisos más amplios de lo necesario en algunos jobs

Se observan `contents: write` y, en algunos workflows, `issues: write`. Son necesarios para guardar históricos o abrir Issues, pero aumentan el impacto de un error en una dependencia o script.

Recomendación: separar jobs de lectura, generación y publicación; usar el mínimo permiso por job. Para el panel diario, revisar si el histórico necesita escribirse diariamente o si puede publicarse mediante un artefacto separado.

### 8. Dependencias de GitHub Actions y Firebase no están fijadas por SHA/versiones completas

Los workflows usan referencias como `actions/checkout@v4`, `actions/setup-python@v5`, y `npx --yes firebase-tools@15`.

Esto es funcional, pero deja el resultado sujeto a cambios futuros de tags o de la última versión disponible dentro del major.

Recomendación: fijar acciones a SHA revisado y fijar `firebase-tools` a una versión concreta. Actualizar de manera deliberada y probar antes de publicar.

### 9. La configuración actual desactiva caché para todo el hosting

`firebase.json` aplica `Cache-Control: no-cache, must-revalidate` a `**`. Eso favorece frescura, pero obliga a validar cada carga y puede empeorar latencia y consumo.

Firebase permite definir cabeceras por patrón. Recomendación:

- HTML principal y `version.json`: validación frecuente/no-cache.
- Archivos estáticos versionados: caché prolongada.
- Si se mantiene todo inline, al menos medir el impacto real antes de cambiar.

La auditoría ya encontró respuestas de 2,19–3,05 s en las cuatro páginas auditadas del sitio real y la portada sobre 3 s. Eso no es exactamente LCP, pero sí justifica medir TTFB/LCP real en móvil antes de afirmar que la optimización terminó.

### 10. La auditoría SEO no cubre toda la seguridad y calidad que el panel recomienda

El auditor principal revisa sitemap, title, description, H1, canonical, alt, lazy-load, JSON-LD y tiempo de respuesta. El inspector manual añade más señales, pero no están integradas en el ciclo semanal principal.

Quedan fuera o parcialmente fuera del auditor automático:

- Cabeceras HTTP reales.
- CSP efectiva.
- robots meta y X-Robots-Tag.
- Open Graph y Twitter Cards.
- `srcset`, dimensiones y peso de imágenes.
- enlaces rotos internos.
- datos estructurados semánticos: teléfono, dirección, `areaServed`, `sameAs` y horarios.
- eventos de conversión reales.

Recomendación: incorporar estas señales por etapas, sin convertir el auditor en un escáner agresivo. Mantener las pausas y el límite de solicitudes.

## UX y producto

### Fortalezas verificadas

- Navegación clara en ocho secciones.
- Tabla filtrable con grupo, dirección, etiqueta, búsqueda mínima, paginación y exportación CSV.
- 170 keywords visibles y 10 frases marcadas al cargar.
- Simulador con presupuesto, días, CPC, contactos y reservas como supuestos explícitos.
- Escenarios conservador, base y optimista con origen del CPC.
- Advertencias visibles de que no se crea campaña ni se cobra.
- Recorrido de 11 pasos con detención antes de publicar.
- Historial local de consultas en vivo limitado a 10.
- La interacción probada en el navegador no mostró errores propios de JavaScript; los únicos errores registrados fueron de una extensión del navegador, no del panel.

### Mejoras recomendadas

1. En cada cifra, mostrar una etiqueta de origen: “Google Ads histórico”, “previsión oficial Google”, “observado en sitio”, “supuesto” o “propuesta IA”.
2. Mostrar una columna o ficha “fecha de vigencia” para pujas y volúmenes.
3. En el simulador, cambiar “Optimista” por “CPC de previsión” y evitar que el nombre sugiera que el resultado comercial será mejor.
4. Añadir botón “Restaurar escenario inicial” después de que el usuario cambie presupuesto/días.
5. Mostrar el límite de la previsión de Google junto al resultado matemático, no solo en un párrafo posterior.
6. En “Ideas de IAs”, diferenciar visualmente ideas no verificadas de recomendaciones respaldadas por datos.
7. En “Mejoras del sitio”, añadir estado: confirmado, pendiente del dueño, requiere acceso o inferencia.
8. Añadir pruebas automatizadas de teclado, filtro, paginación, exportación, simulador y layout móvil; hoy las pruebas del repositorio son principalmente unitarias de Python.

## Datos reales confirmados y datos que no deben presentarse como confirmados

### Confirmado en esta revisión

- Repositorio privado `oviedoem/ubertransfer-ops`, rama `main`.
- Panel publicado y accesible sin login.
- 170 filas en el archivo de keywords.
- Exportación de keywords del Planificador fechada 29-09-2026.
- Previsión de Google almacenada para 1–31 octubre 2026, plan `1441122025`.
- 17/17 verificaciones internas correctas en la interfaz revisada.
- 10 frases marcadas inicialmente.
- La auditoría técnica almacenada tiene cuatro páginas y estados HTTP 200.
- Search Console y GA4 aparecen como desconectados.
- El sitio auditado presenta tiempos almacenados de 2,19–3,05 s y avisos SEO medidos.
- El panel no realiza gasto ni crea campañas.

### No confirmado todavía

- Número real de sesiones, contactos, llamadas, chats o reservas.
- Tasa de conversión de WhatsApp.
- Costo por lead o costo por reserva.
- Comunas y rutas realmente atendidas.
- Tarifas vigentes, horarios reales, flota y descuentos.
- Que todas las frases sean rentables o apropiadas para contratar.
- Que el sitio tenga buen LCP/Core Web Vitals en usuarios reales.
- Que GTM y gtag estén contando doble.
- Que el nombre “UberTransfer” pueda utilizarse sin riesgo de marca.

## Plan de trabajo recomendado

### P0 — corregir antes de conectar datos reales

- Corregir GA4 `sessions`.
- Hacer fallar la auditoría cuando no descubre páginas.
- Decidir si el panel será privado o público y aplicar esa decisión.
- Generar alerta visible si el workflow SEO se omite por falta de credenciales.
- Revisar permisos y fijado de dependencias de workflows.

### P1 — siguiente iteración

- Integrar inspector de contenido y cabeceras al reporte semanal.
- Medir TTFB y LCP por móvil/desktop; no confundirlos con el tiempo de descarga HTML.
- Añadir eventos de conversión: WhatsApp, teléfono y correo, cada uno separado.
- Conectar GA4/Search Console solo con permisos de lectura.
- Rediseñar el resultado del simulador para distinguir extrapolación matemática de previsión oficial.

### P2 — mejora de producto

- Pruebas E2E del panel en 375, 820 y 1440 px.
- Estados de confianza por cada recomendación.
- Histórico visual de auditorías y cambios de datos.
- Módulo futuro de términos de búsqueda y negativas cuando exista una campaña real.
- Monitor externo de disponibilidad, si se aprueba, sin hacer sondeos agresivos.

## Fuentes técnicas consultadas

- Código y datos: [repositorio UberTransfer Ops](https://github.com/oviedoem/ubertransfer-ops).
- Métrica oficial `sessions` de Google Analytics Data API: [Google for Developers](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).
- Medición de conversiones web y llamadas en Google Ads: [Google Ads Help](https://support.google.com/google-ads/answer/1722054?hl=en).
- Umbral recomendado para LCP: [web.dev — Largest Contentful Paint](https://web.dev/articles/lcp).
- Cabeceras y caché de Firebase Hosting: [Firebase Hosting configuration](https://firebase.google.com/docs/hosting/full-config).

## Conclusión

El panel ya es útil como herramienta educativa y de investigación. La siguiente mejora no debería ser agregar más ideas de IA o más keywords, sino aumentar la confiabilidad operacional: acceso correcto, medición GA4 correcta, fallos explícitos, fuentes separadas y simulaciones que no parezcan pronósticos reales.

