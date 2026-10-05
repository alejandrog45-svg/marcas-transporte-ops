# 02_respuesta_chatgpt.md — GPT-5.6 Sol — 30-09-2026

## 1. Recomendación

**Recomiendo combinar A + B, no C al inicio.**

**[VERIFICADO: datos entregados en 01_CONSULTA.md]** Aereostar ya tiene una campaña de Búsqueda activa desde octubre de 2025, mientras UberTransfer todavía no anuncia. Además, la demanda medida está fuertemente concentrada en aeropuerto; corporativo/bodas/eventos tiene mucho menos volumen.

**[SUPUESTO]** Hasta revisar resultados reales de Aereostar, mantendría **Aereostar como única marca que puja por búsquedas genéricas de aeropuerto**. UberTransfer se reservaría para su propia marca y para corporativo, bodas/eventos, turismo, privados/compartidos y destinos donde su propuesta sea realmente diferenciada. Esto reduce solapamiento y evita iniciar dos cuentas contra la misma intención sin evidencia de que aporte valor.

### Primeras 2 semanas
1. No publicar UberTransfer todavía.
2. Obtener el informe de Aereostar de los últimos 3–6 meses: términos de búsqueda, coste, clics, conversiones y coste/conversión.
3. Definir conversiones equivalentes para ambas marcas (por ejemplo, contacto/lead válido) antes de comparar.
4. Construir un mapa maestro: **intención/consulta → marca asignada**.
5. Preparar negativas cruzadas y campañas de marca, pero activarlas solo con aprobación.
6. Si Aereostar no tiene conversiones fiables, corregir medición antes de decidir qué marca debe llevar aeropuerto.

No recomiendo C (“mitad de palabras para cada marca durante dos semanas”) como primera prueba: **[SUPUESTO]** con poco presupuesto y conversiones desconocidas puede comparar mezclas distintas de intención en vez de comparar limpiamente las marcas.

## 2. Política real de Google y estructura de cuentas

**[VERIFICADO: https://support.google.com/adspolicy/answer/15936768]** La política vigente de Google Ads se denomina **Unfair advantage** dentro de “Abusing the ad network”. Prohíbe usar la red para obtener una ventaja injusta en la subasta. Entre sus ejemplos figura intentar mostrar más de un anuncio de un negocio, app o sitio en una misma ubicación publicitaria. Google también indica que cada sitio/app promocionado debe aportar valor distinto y aconseja evitar productos y precios similares en destinos relacionados.

Por tanto, **dos dominios y dos cuentas no convierten automáticamente la situación en válida**. **[SUPUESTO]** Si UberTransfer y Aereostar pertenecen al mismo dueño, apuntan a la misma intención y ofrecen servicios muy similares, hacerlas competir simultáneamente para ocupar más espacio puede aumentar el riesgo de revisión por esta política. La aplicación concreta la decide Google.

**[VERIFICADO: https://support.google.com/google-ads/answer/6139186]** Conviene mantener **dos cuentas cliente separadas**, una por marca, y vincularlas a **una cuenta de administrador (MCC)**. El MCC permite administrar y comparar varias cuentas desde un panel; vincular una cuenta existente no borra ni modifica su historial. El MCC **no elimina** las obligaciones de política.

## 3. Marca propia y negativas cruzadas

**[SUPUESTO]** Estructura práctica:
- Aereostar: campaña de marca `Aereostar` y, mientras sea la asignada, genéricos de aeropuerto.
- UberTransfer: campaña de marca `UberTransfer` y sus categorías diferenciadas.
- En campañas genéricas, excluir la marca contraria cuando sea necesario para evitar cruces no deseados.
- No usar una negativa global de “aeropuerto” en UberTransfer si esa palabra también aparece en consultas legítimas de su propia marca o servicios permitidos; aplicar negativas por campaña según el mapa de intenciones.
- Revisar **términos de búsqueda reales**, no solo la lista de palabras clave, porque las concordancias pueden activar consultas no previstas.

### “Uber” dentro de “UberTransfer”
**[VERIFICADO: https://support.google.com/adspolicy/answer/6118]** Google no restringe, por su política de marcas, el mero uso de una marca ajena **como palabra clave** ni su presencia en el dominio de segundo nivel de la URL visible. Sí puede restringir el uso de una marca en el **texto del anuncio** de un competidor directo o cuando resulte confuso, engañoso o equívoco, tras una reclamación del titular.

**[SUPUESTO]** No asumiría que el nombre “UberTransfer” autoriza a usar “Uber” libremente en anuncios. Antes de lanzar, comprobaría la situación jurídica de la denominación y cualquier restricción/reclamación dentro de Google Ads. No sé, con los datos entregados, si existe autorización o derecho marcario aplicable en Chile.

## 4. Medición separada

**[VERIFICADO: https://support.google.com/analytics/answer/14183469]** GA4 permite crear propiedades y flujos web. **[SUPUESTO]** Para máxima claridad operativa aquí usaría **una propiedad GA4 separada por marca/dominio**: UberTransfer ↔ su GA4 ↔ su cuenta Google Ads; Aereostar ↔ su GA4 ↔ su cuenta Google Ads.

**[VERIFICADO: https://support.google.com/google-ads/answer/16560108]** Para importar conversiones desde Analytics, la propiedad correcta debe estar vinculada a Google Ads y el evento debe estar marcado como evento clave. Evitar doble etiquetado, porque puede duplicar conversiones.

Definir en ambas marcas la misma taxonomía de negocio: lead/formulario, clic de WhatsApp, llamada y, si es posible, **reserva/venta confirmada**. **[SUPUESTO]** El KPI decisivo debería acercarse a negocio real (lead válido/reserva), no quedarse solo en clics.

## 5. Cómo decidir con pocos datos

**[SUPUESTO]** Primero usar datos históricos de Aereostar como línea base. Si después se necesita una prueba entre marcas, no hacerlas pujar simultáneamente por la misma consulta. Hacer una prueba **secuencial**, con conjuntos equivalentes de intención, ubicación, horario y presupuesto, manteniendo una sola marca asignada a cada búsqueda durante cada periodo.

Medir: gasto, clics, CTR y CPC como diagnóstico; conversiones válidas, tasa de conversión y coste por conversión como decisión; y, si Rafael dispone del dato, reservas/ventas e ingreso o margen por lead.

No fijaría ahora un umbral numérico de ganador: **[SUPUESTO]** faltan volumen de conversiones, margen y calidad de leads. Si hay muy pocas conversiones, ampliar el periodo antes de decidir; dos semanas son una ventana inicial, no garantía de significancia.

## 6. Seis datos que pedir a Rafael

1. **[VERIFICADO: necesario para evaluar histórico]** Exportación de Aereostar de los últimos 3–6 meses: campañas, términos de búsqueda, coste, clics y conversiones.
2. **[SUPUESTO]** Qué acciones están configuradas hoy como conversiones y cuáles representan clientes reales.
3. **[SUPUESTO]** Reservas/ventas atribuibles y valor o margen aproximado por servicio/marca.
4. **[SUPUESTO]** Cobertura geográfica, horarios y servicios exactos que cada marca quiere vender.
5. **[SUPUESTO]** Presupuesto máximo mensual/diario aprobado para cada marca.
6. **[SUPUESTO]** Situación del nombre “UberTransfer”: titularidad/registro/autorización relevante y si ha habido avisos de Google o del titular de “Uber”.

## 7. Qué NO hacer

- **[VERIFICADO: política Unfair advantage]** No intentar ocupar más de una posición publicitaria para el mismo negocio mediante cuentas/destinos relacionados.
- **[SUPUESTO]** No lanzar UberTransfer copiando las mismas 170 frases de Aereostar.
- **[SUPUESTO]** No comparar marcas solo por CTR o CPC; medir conversiones y calidad.
- **[SUPUESTO]** No mezclar ambos dominios en una medición que impida atribuir resultados por marca.
- **[SUPUESTO]** No cambiar campañas cada pocos días si todavía no hay datos suficientes.
- **[VERIFICADO: política de marcas]** No asumir que poder pujar por una palabra de marca significa poder usarla sin restricciones en el texto del anuncio.

## Nivel de confianza

**Recomendación: alta** en separar intenciones, cuentas y medición y evitar solapamiento deliberado; **media** respecto de qué marca debe quedarse definitivamente con aeropuerto, porque faltan los resultados reales de Aereostar y datos de conversiones/ventas.

Las políticas son sensibles a cambios. Confirmar las páginas oficiales siguientes inmediatamente antes de publicar campañas.

## Fuentes

- Google Ads — Unfair advantage: https://support.google.com/adspolicy/answer/15936768
- Google Ads — Abusing the ad network: https://support.google.com/adspolicy/answer/6020954
- Google Ads — Trademarks: https://support.google.com/adspolicy/answer/6118
- Google Ads — Acerca de las cuentas de administrador (MCC): https://support.google.com/google-ads/answer/6139186
- Google Ads — Configurar conversiones web: https://support.google.com/google-ads/answer/16560108
- Google Analytics — Configurar Analytics para un sitio/app: https://support.google.com/analytics/answer/14183469
