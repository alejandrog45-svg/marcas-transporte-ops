# REPORTE COMPLETO — ubertransfer-ops (para Claude Code en PC local)

Fecha: 2026-09-30 · Panel: https://ubertransfer-ops.web.app/ · Carpeta local: `ubertransfer-ops` (rama main)
Origen: auditoría de SOLO LECTURA hecha en el navegador (Claude Cowork). No se modificó código, GitHub, Firebase ni credenciales.
Lo de abajo son observaciones desde el navegador: VERIFICAR cada una contra el código local antes de cambiar nada.

## 0. Reglas obligatorias para esta sesión
- Leer AGENTS.md y CLAUDE.md primero. Activar skills: ahorro de tokens, prevención, Safe Change y regla anti-retroceso.
- Declarar TOCO / RAZÓN / NO-TOCO antes de cada cambio. Una tarea a la vez, un prompt una función.
- Nunca tocar credenciales. Nunca usar disco D. Proyecto a costo cero (Firebase Hosting gratuito).
- Cada cambio: deploy + commit; confirmar en carpeta local, GitHub y datos. Al cierre: guardar estado-sesión y actualizar CLAUDE.md y carpeta conocimiento del negocio (disco E).
- Re-ejecutar las 17 verificaciones del panel tras cada cambio (deben seguir 17/17).

## 1. Resumen ejecutivo
El panel funciona y sus datos son coherentes (170 frases, 10 marcadas, 5.000 CLP, 1140 clics; 17/17 verificaciones OK). Hay 1 error real de lógica (Simulador), 1 debilidad del botón "Consultar en vivo" (no valida el estado HTTP), 1 confusión de UX con las fechas y 1 error menor de consola (favicon 404). El 503 visto en red NO se confirmó como caída del sitio: ubertransfer.cl cargó bien al leerlo aparte.

## 2. Respuestas a las preguntas originales
- **¿Dónde queda el registro de la consulta?** Solo en localStorage del navegador, clave `ut_live_hist` (últimas 10; campos: at, ok, fail, total, site, ver, sha). No está en Firestore ni en GitHub: se pierde al limpiar el navegador y no se ve desde otro equipo.
- **¿Por qué las fechas no cambian?** Es por diseño: "Consulta:" es un reloj que avanza cada segundo (no es la hora de la consulta); "Datos de Google" (29-09 22:05:59) y "Auditoría del sitio" (30-09 02:43:38) son instantáneas fijas; el botón no consulta Google Ads/Search Console/GA4. La hora real del clic está en "Última consulta en vivo" (sí cambia).
- **Error 404 de la consola:** `GET /favicon.ico`. No hay `<link rel="icon">`. No afecta el funcionamiento.
- **Datos consistentes en palabras clave:** sí. Grupos 142+5+23=170; direcciones 23+7+140=170; etiquetas 154 utilizables + 8 marcas competidoras + 8 fuera de tema = 170. Las 10 frases marcadas coinciden en tarjetas, Simulador, Borrador y verificaciones.

## 3. Hallazgos a corregir (orden sugerido, una tarea a la vez)
1. **Favicon 404** — Agregar `favicon.ico` en `public/` o `<link rel="icon" href="data:,">` en el `<head>`. Criterio: consola sin 404.
2. **Etiqueta "Consulta:"** — Renombrar a "Hora actual:" (o mostrar junto a "Última consulta en vivo") para que no parezca la hora de la consulta.
3. **Simulador: texto "clics en 31 días" ignora el campo `#dias`** — con Días=28 o 30 el texto sigue diciendo 31 y 1178; la tarjeta sí cambia (30→1140, 31→1178, 28→1064). Hacer que el texto use `#dias`. Nota: los clics/día se calculan con parte entera (38 × días); confirmar que es intencional.
4. **Simulador: presupuesto 0 se ignora sin aviso** (conserva el valor anterior). Mostrar aviso o mínimo explícito.
5. **Formato de miles** — la tarjeta muestra "1140", otras partes "1.140". Unificar.
6. **Rango "1178 – 1178"** (mínimo = máximo) — mostrar un solo valor o revisar por qué no hay rango.
7. **Botón "Consultar en vivo" / probe "Medir ahora"** — Hoy cuentan cualquier respuesta como éxito ("Respondió 3 de 3", "al día"). En la red el navegador registró `GET https://ubertransfer.cl/?_=...` con estado 503 (6 de 6) y `HEAD /` del panel con 503, pero al leer ubertransfer.cl aparte cargó normal. Probable artefacto de una petición de origen cruzado sin lectura de estado (no-cors). Revisar en `liveRun`/probe: si no se puede leer el estado HTTP, decirlo en pantalla; si se puede, tratar 5xx como fallo. Tiempos medidos: 2779, 3150 ms (consulta) y 5823 · 3056 · 3215 ms (probe).
8. **Historial de consultas** — Opcional: guardarlo también en Firestore (plan gratuito, proyecto `ferreteria-oviedo` u otro de UberTransfer según AGENTS.md; confirmar) para verlo desde otros equipos. Solo si se decide; no tocar credenciales.
9. **Tabla de frases** — Sin indicador "Página X de Y" (hay 17 páginas de 10). "Ordenar: puja baja" deja primero las frases sin dato (—): mandar los vacíos al final.
10. **Verificaciones** — Añadir chequeo de que el texto del Simulador usa los mismos días que la tarjeta, y de que el probe lee el estado HTTP.

## 4. Pendientes que NO son del panel (decisión del dueño / otras tareas)
- Search Console y GA4 sin conectar: el flujo «SEO diario» no extrae datos (faltan GOOGLE_SA_JSON y GA4_PROPERTY_ID). Son secretos: NO crearlos ni tocarlos sin orden explícita del dueño.
- Ideas de IAs: la sección "qué revisar cada semana" de Gemini quedó sin leer.
- Auditoría del sitio (pestaña Mejoras, 16 ítems): `/tarifas/` da 404 (el menú apunta a /#tarifas); horario incoherente (schema 09:00–17:00 vs texto "24 horas, los 7 días", confirmado en el sitio); home 3,24 s; 39 imágenes sin lazy-load; titles 74–92 car. (ideal ≤60); description 181 car. en /servicio; GTM (GTM-WLPJJD4J) + gtag (G-26K0MDTFY1) posible conteo doble; confirmar eventos click_whatsapp, click_phone, lead_submit; no hay formulario (contacto por WhatsApp, teléfono y correo); píxel de Meta detectado; schema sin teléfono, dirección ni areaServed; revisar política de marcas de Google Ads con la marca "Uber" antes de anunciar.
- Estado de la campaña: SIMULACIÓN; nada creado en Google Ads. Presupuesto, pago y verificación de identidad quedan en manos del dueño.

## 5. Lo que se probó y funciona (no tocar: regla anti-retroceso)
Búsqueda, filtros (grupo, dirección, etiqueta), mínimo de volumen, 4 órdenes, tamaños de página (10/25/50/100/Todas), paginación (prev/next se deshabilitan en los extremos), "Marcar utilizables ≥500" (10→22, revertido), Simulador (presupuesto, escenarios, contactos/reservas: 150 clics×5 %=7,5; ×10 %=0,8 ✓), Borrador (estructura = 10 frases; anuncio 28/30, 20/30, 71/90), Recorrido (11 pasos) y Mejoras (16 ítems) con casillas guardadas en localStorage (`done`), Copiar estructura, historial de consultas (2 entradas al probar, ahora ya existentes en el navegador), 17/17 verificaciones, sin imágenes rotas en ninguna pestaña.
### 5.1 Pruebas completadas después (Tarea 4)
Todo revertido: localStorage quedó como al inicio (`ut_live_hist`, `sel`=10 frases, `tab`); tarjetas 170 / 10.
- **Exportar CSV** (`#btn_csv`): capturado en memoria, sin descargar. Archivo `palabras_clave.csv`, 1549 bytes, separador `;`, sin BOM UTF-8. Cabecera: Frase;Busquedas_mes;Competencia;Puja_baja_CLP;Puja_alta_CLP;Grupo;Fuente;Datos_exportados;Consultado_el. Exporta SOLO las 10 frases marcadas (no las 170), y la columna "Consultado_el" sí lleva la hora real del clic (30-09-2026 14:04:19). Hallazgo: el botón dice "Exportar CSV" sin aclarar que es solo lo marcado; sin BOM, Excel puede romper acentos si aparecen.
- **Agregar palabra clave** (`#btn_add`): usa `prompt()` del navegador ("Nueva frase (sin volumen ni puja: no vienen de Google)"). Con la frase de prueba "zz prueba panel": se guarda en localStorage clave `custom`, se marca sola (10→11 marcadas), sube "frases analizadas" a 171 (mezcla frases propias con datos de Google bajo la etiqueta "Planificador de Google"), fila con "—" en volumen y pujas, grupo "Otros". No hay botón para borrarla. Las 17 verificaciones siguieron en OK (cuentan 170 del archivo). Prueba borrada.
- **Copiar resumen** (`#simcopy`) y **Copiar estructura** (`#cp`): funcionan (probado capturando el texto, sin tocar el portapapeles real). El resumen repite "Clics al mes: 1140 – 1140" (rango colapsado) y usa "Consultado:" con la hora actual.
- **Palabras negativas** (`#neg`, 20 líneas): el campo se puede editar (20→21 líneas), pero NO se guarda en localStorage: se pierde al recargar aunque el título dice "editable". Hallazgo a corregir o a aclarar.
- **Recorrido**: 11 pasos, coherentes con el resto (teléfono +56 9 4996 9267 coincide con el sitio; ejemplo 4,6 mil CLP/día ≈ 140 mil/mes = previsión de Google, distinto de los 5.000 CLP/día del simulador, ambos rotulados). Ubicación (RM o todo Chile), presupuesto y horario siguen PENDIENTES del dueño.
- **Guía / Ideas de IAs**: sin inconsistencias numéricas; las ideas de IAs están rotuladas "sin verificar".
- **Accesibilidad / metadatos**: `lang="es"`, viewport correcto, 12 reglas @media responsivas (640/768/1024/1280/1536 px), `robots: noindex, nofollow, noarchive` (correcto para un panel privado), 0 imágenes sin alt, 0 botones sin etiqueta; 6 campos sin etiqueta ni placeholder (menor); sin meta description ni manifest (irrelevante para panel privado).
- **Limitación honesta**: el tamaño móvil real no se pudo emular desde esta sesión (el navegador con DevTools acoplado no cambió el ancho de página). Solo se confirmó que existen las reglas responsivas. Probar en un celular real o con la emulación de dispositivo de DevTools.

### 5.2 Hallazgos adicionales a corregir (continúan la numeración de la sección 3)
11. Palabras negativas "editables" no persisten: guardarlas (localStorage o Firestore) o retirar la palabra "editable".
12. "Agregar palabra clave": permitir borrar frases propias y no sumarlas a "Frases analizadas" del Planificador (o rotularlas como propias).
13. "Exportar CSV": aclarar el nombre ("Exportar frases marcadas") o dar la opción de exportar las 170; considerar BOM UTF-8.
14. Campos sin etiqueta (6): agregar aria-label.

## 6. Datos de referencia (no cambiar)
- Fuente: Planificador de Google (Chile), archivo Keyword Stats, SHA-256 `32918ae9347c…`; datos del 29-09-2026 22:05:59; auditoría 30-09-2026 02:43:38.
- CPC medio previsión Google ≈ 130 CLP; 38 clics/día; 1140 clics (30 días) / 1178 (31 días); previsión Google ≈ 1.100 clics, ~4.600 CLP/día, 140.000 CLP/mes.
- localStorage del panel: `ut_live_hist` (historial), `sel` (10 frases marcadas), `tab`, `done` (checks de Mejoras/Recorrido, se crea al marcar), `ps` (tamaño de página, se crea al cambiar).
- 10 frases marcadas: transfer aeropuerto santiago · traslado aeropuerto santiago · taxi aeropuerto santiago · transfer aeropuerto santiago valor · transfer compartido aeropuerto santiago · transfer santiago aeropuerto · transfer aeropuerto santiago chile · van aeropuerto santiago · transfer barato aeropuerto santiago · transfer vip santiago.

```

