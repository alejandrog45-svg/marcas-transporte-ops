# Tips de Rafael, datos del negocio y preguntas abiertas (2026-10-08)

Resumen de la revisión completa de `marcas-transporte-ops`, `DATA TRANSPORTE` y `Plataformas-anuncios-local`. Cuenta de trabajo: Google Ads **203-550-4421** (ubertranfer, ubertransfer436@gmail.com).

## 1. Qué dijo Rafael (literal)

Fuente: `docs/recomendaciones_rafael_20260930.md` (audios y mensajes de WhatsApp del 30-09, leídos por la transcripción automática, puede tener errores). Los audios y capturas originales no están guardados.

1. La campaña debe ser de **Búsqueda**. No puede ser inteligente ni de Máximo rendimiento.
2. Hay una forma de ponerla en **modo experto**. El nombre exacto del botón no está verificado en pantalla.
3. En la lista de campañas debe aparecer **BÚSQUEDA** (su captura: "Campaña Aereostar Octubre 2025 · BÚSQUEDA").
4. Hay que agregar más palabras clave.
5. Frases pedidas: "transfer eventos privados", "transfer matrimonios", "transporte corporativo". Google las mide con 0 a 100 búsquedas al mes cada una. "matrimonio" sí aparece medida, "boda" no.

Dato suyo casi textual: el transporte sirve para todo tipo de rubro, no solo aeropuerto.

No existe ninguna instrucción literal de Rafael sobre presupuesto, ubicación, horarios, textos de anuncios ni promos.

## 2. Lo que NO es de Rafael

Reglas o propuestas del dueño del proyecto, de Claude o de las IAs. No atribuirlas a Rafael:

- Nada se activa ni se paga sin aprobación. Una tarea a la vez.
- Estructura de 3 grupos (Aeropuerto / Eventos y matrimonios / Corporativo), concordancia de frase y exacta, solo Red de Búsqueda, Maximizar clics.
- Negativas iniciales y reemplazo de "trabajo" y "bus" por frases más específicas.
- "Una frase, un dueño" y el reparto provisional Aereostar = aeropuerto, UberTransfer = marca y rubros.
- Presupuesto de ~$4.600 al día (previsión de Google, no decisión).
- No usar "Uber" suelto en los textos de anuncios (INAPI: UBER registrada por Uber Technologies, clase 39).

## 3. Datos reales del negocio (viajes 1 may a 5 oct 2026, `data/data.json`)

| Dato | Valor |
|---|---|
| Viajes realizados | 2.334 |
| Ingresos cobrados | $85.764.250 |
| Ticket promedio | $39.946 |
| Pasajeros | 6.057 |
| Hacia el aeropuerto | 1.377 viajes (59%) |
| Desde el aeropuerto | 475 viajes |
| Mes pico | Septiembre: 502 viajes, $17,6 M |
| Demanda por hora | Madrugada 02:00-08:00; pico lunes 03:00-05:00; fin de semana 04:00-06:00; segundo bloque 23:00-00:00; valle 10:00-15:00 |
| Sectores con más viajes | Santiago Centro 230, Las Condes 227, Providencia 216, Ñuñoa 182 |
| Clientes únicos / recurrentes | 1.459 / 424 (los recurrentes hacen el 54% de los viajes) |
| Gasto Google Ads ene-ago | $15.026.850 (entre 6% y 16% de la venta, salvo mayo mal cargado) |
| Margen mensual (venta menos gasto) | Negativo o cercano a cero en los meses con datos |

Hallazgos en los comentarios de la planilla:

- Hay **cuatro marcas o canales**: TaxiTransfer (mayor volumen de llamadas), Aereostar, UberTransfer y Compartido. Hubo campañas anteriores "TAXITRANSFER" y "COMPARTIDOS".
- Ofertas reales: cambio a compartido por $16.000 o $22.000, sobreequipaje $6.000, ida y vuelta, empresas con factura y precios más IVA, convenios nocturnos semanales.
- Los externos cuestan entre $28.000 y $100.000 por viaje y a veces no hay disponibles en los picos.

## 4. Contradicciones y limitaciones

- Cuenta definida: **203-550-4421** (decisión del usuario, 2026-10-08). No aparece en ningún archivo antiguo; los archivos viejos citan la 926-538-5719, ahora descartada. Los datos del Planificador y la previsión salieron de esa cuenta descartada, así que son referencia y no historial de la 203-550-4421.
- "UberTransfer no lanza frases de aeropuerto" (regla provisional) choca con el pedido de ampliar palabras clave y con las 170 frases de aeropuerto.
- La planilla anual y los viajes no coinciden (mayo $7,6 M frente a $17,1 M). Para ROAS usar los viajes, no la planilla anual.
- En la planilla "Rafael" figura como el conductor con más viajes. Ningún archivo confirma que sea el dueño.
- Horario: el sitio dice 24 horas, el schema dice 09:00-17:00, y las tarifas por horario dejan sin cubrir 18:00-19:30 y 06:00-07:30.
- Seguridad: hay una API key de Stitch en texto plano en una carpeta ignorada por git, y la clave del Apps Script apareció en una captura. Conviene rotarlas.

## 5. Preguntas abiertas para Rafael

### Cuentas y marcas
1. ~~¿Qué cuenta se usa?~~ **RESUELTA (2026-10-08, indicado por el usuario):** se trabaja solo con la cuenta **203-550-4421** (ubertranfer). Se descartan la 926-538-5719, la "Aerostar" 465-674-2227 y la cancelada "Ubertransfer - Amadigital.cl" 371-706-4621. No se opera ninguna de ellas.
2. ¿Quién lleva las frases de aeropuerto, UberTransfer o Aereostar?
3. ¿TaxiTransfer y Compartido tienen campaña propia o entran en esta? ¿Qué sitio y teléfono usa cada marca?
4. ¿Quién administra hoy las campañas de Aereostar y qué resultados tuvo "Campaña Aereostar Octubre 2025" (3 a 6 meses de historial)?
5. ¿Se acepta no usar "Uber" suelto en los anuncios y consultar a un abogado antes de usar el nombre completo?

### Servicios, precios y datos
6. ¿UberTransfer ofrece de verdad eventos privados, matrimonios y corporativo? ¿Con qué vehículos y capacidad, y a tarifa fija o por cotización? ¿Hay una página del sitio para cada rubro?
7. ¿Cuáles son las tarifas oficiales por ruta y horario? ¿Qué se cobra entre 18:00 y 19:30 y entre 06:00 y 07:30?
8. ¿La promoción de $5.000 de descuento en ida y retorno sigue vigente y se puede publicar en los anuncios?
9. ¿Cuál es el horario real: 24 horas, los 7 días, u otro?
10. ¿Cuál es la flota real y su capacidad (Sorento, Carnival, Mercedes, Sonata)? ¿Se anuncia pet friendly?
11. ¿Se anuncia el servicio compartido y a qué precio? ¿Se mencionan sobreequipaje y facturación con IVA para empresas?
12. ¿Se usa el mismo teléfono y WhatsApp en todas las marcas? ¿Cuál es el de Aereostar?

### Campaña
13. ¿Cuál es el presupuesto diario y el tope por marca? Referencias: previsión de Google ~$4.600 al día, el asistente sugiere $15.817, y el gasto histórico fue de $1,5 M a $2,8 M al mes.
14. ¿La ubicación es Región Metropolitana o todo Chile? ¿Qué comunas y rutas son prioritarias, y se incluyen destinos fuera de Santiago?
15. ¿Los anuncios van solo en español o también en inglés?
16. ¿Los anuncios corren las 24 horas o se prioriza la madrugada de 02:00 a 08:00, que es el pico de viajes?
17. ¿Se prueba "boda" además de "matrimonio"?
18. ¿Qué cuenta como conversión: llamada, WhatsApp, o ambas?
19. ¿Dónde está exactamente la opción de "modo experto" que mencionó? ¿Puede mandar una captura?
20. ¿Quién aprueba los textos de los anuncios antes de cargarlos?

### Accesos y pagos
21. ¿Puede dar acceso a Google Analytics (G-26K0MDTFY1) y a Search Console? ¿Quién administra Tag Manager, y se corrige el doble conteo entre GTM y gtag?
22. ¿Quién paga la campaña y desde qué perfil de pagos? ¿Se quiere aprovechar la promoción de USD 350 en créditos que ofrece el asistente (vence el 7 dic 2026)?

## 5.1 Respuestas de Rafael (2026-10-08, dictadas por el usuario con Rafael presente)

- **Objetivo:** campaña de **Búsqueda** para que **llamen y escriban por WhatsApp** (responde la pregunta 18: dos conversiones, llamada y WhatsApp).
- **Palabras clave:** transporte aeropuerto, transfer, aeropuerto, eventos privados, transporte corporativo, matrimonios, turismo, viña tours (dictado "viñas tours").
- **Ubicación:** Región Metropolitana, Viña del Mar, Rancagua, Los Andes y Melipilla. Dentro de eso, priorizar por el **ranking de viajes del Excel**: Santiago Centro 230, Las Condes 227, Providencia 216, Ñuñoa 182, Quilicura 161 (convenio de grupos), La Florida 82, Maipú 81, Vitacura 70, Colina 68, San Bernardo 64. Viña del Mar, Rancagua, Los Andes y Melipilla no figuran como sectores en el Excel.
- **Idiomas:** español e inglés.
- **Redes:** solo Búsqueda de Google (sin socios ni Display).
- **URL final:** `https://ubertransfer.cl/`.

- **Presupuesto (decidido 2026-10-08):** opción A, **CLP 15.000 al día**, como prueba de la campaña. Aplicado en el borrador de la cuenta 203-550-4421.
- **Teléfono y WhatsApp (decidido 2026-10-08):** **+56 9 4996 9267** para ambos. El mismo número figuró como "sin verificar" y rechazado en la campaña antigua de Amadigital, así que hay que verificarlo.

- **Decisiones adicionales (2026-10-08):** textos de anuncios los propone Claude (ver `propuesta_textos_anuncios.md`); página de destino `https://ubertransfer.cl/`; horario de anuncios **24 horas** (reemplazado después por 08:00 a 22:30, ver 5.2); **Aereostar no entra** en esta campaña y solo se trabaja UberTransfer (no revisar otras cuentas); la pregunta de la marca "Uber" se descarta: se usa el nombre completo "UberTransfer".
- **Cargado en el borrador:** palabras clave del grupo aeropuerto, ubicaciones (Región Metropolitana, Viña del Mar, Rancagua, Los Andes; Melipilla está dentro de la Región Metropolitana), idiomas español e inglés, solo Red de Búsqueda de Google, presupuesto CLP 15.000 al día.

Notas de Claude: (a) "transfer" y "aeropuerto" solas son muy amplias, usarlas solo en concordancia exacta o dentro de frases; (b) al usar `ubertransfer.cl` para frases de aeropuerto, queda implícito que UberTransfer las lleva (pregunta 2), pendiente de confirmar expresamente; (c) turismo y viña tours miden poco volumen en el Planificador (0 a 10 al mes en "turismo"); (d) las comunas de Viña, Rancagua, Los Andes y Melipilla necesitan tarifa y confirmación de que se atienden.

## 5.2 Campaña publicada y horario (2026-10-08)

- La campaña de la cuenta 203-550-4421 ("Campaign #1") fue pagada y quedó **habilitada**, con presupuesto CLP 15.000 al día.
- **Horario (según Rafael): todos los días de 08:00 a 22:30**, hora de Chile. Se configuró en Google Ads, en Públicos, palabras clave y contenido > Programación de anuncios. Reemplaza al "24 horas" anterior. Ojo: la demanda real se concentra de 02:00 a 08:00, tramo que ahora queda sin anuncios.
- Regla del usuario: **el horario solo va en Google Ads; los textos de los anuncios no llevan horarios** ni "24 horas". Los títulos 3 y 5 y las descripciones 1 y 4 se cambiaron en consecuencia (ver `propuesta_textos_anuncios.md`).
- Pendiente: verificar el teléfono +56 9 4996 9267 y las conversiones.

## 6. Estado del borrador en Google Ads (cuenta 203-550-4421, histórico previo a publicar)

Borrador de Búsqueda sin activar, detenido antes del pago. URL `https://ubertransfer.cl/`, 6 palabras clave de aeropuerto (frase y exacta), 6 títulos, 2 descripciones, solo Red de Búsqueda, estrategia Clics, presupuesto de CLP 4.600 al día. Los textos y las frases son provisionales hasta resolver las preguntas anteriores.
