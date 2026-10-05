# 04_respuesta_meta.md — Meta AI (Muse Spark, 2026-09-30)

## 1. Recomendación concreta: B + A (híbrida) — Una marca lidera aeropuerto

**Recomiendo B como base, con A como complemento.** [SUPUESTO: con 170 frases de aeropuerto concentrando 1.000-10.000 búsquedas/mes vs 10-100 en otros rubros, pelear por las mismas frases canibaliza presupuesto]. No recomiendo C porque dividir 1.100 clics previstos en dos mitades rompe aprendizaje y duplica costo de prueba [VERIFICADO: Previsión Google del archivo].

**Decisión:** Aereostar lidera aeropuerto (ya tiene campaña desde oct 2025). UberTransfer = corporativo, bodas/eventos, turismo, compartidos, privados fuera de Santiago + solo marca propia. [SUPUESTO: Aereostar ya tiene historial; cambiar líder borraría datos].

**Primeras 2 semanas:**
- Día 1-2: Auditar Aereostar (estructura, coincidencias, conversiones). Pausar palabras de rubros no-aeropuerto en Aereostar.
- Día 3: Crear lista de 170 frases aeropuerto en negativo exacto para UberTransfer. Crear campañas de marca propia en ambas cuentas [VERIFICADO: https://support.google.com/adspolicy/answer/15936768 - una frase un dueño].
- Día 4-7: Lanzar en UberTransfer solo: 2 campañas Búsqueda (1 corporativo/ejecutivo, 1 bodas/eventos) + campaña marca "ubertransfer". Presupuesto inicial mínimo, solo Chile, concordancia frase/exacta.
- Semana 2: Medir CTR, CPC real vs $269-$907 estimado, tasa consulta. Reunión con Rafael para decidir si aeropuerto queda 100% en Aereostar.

## 2. Política real de Google sobre double serving

**Nombre actual:** Ya no es "doble publicación" como política separada. Desde 2012 se fusionó en **Ventaja desleal (Unfair advantage)** dentro de "Uso inadecuado de la red publicitaria". [VERIFICADO: https://support.google.com/adspolicy/answer/15936768]

**Qué dice hoy:** "No se permite: Usar la red de Google para obtener ventaja de tráfico injusta sobre otros participantes. Ejemplos: Afiliados que violan reglas; intentar mostrar más de un anuncio de tu empresa, app o sitio en una sola ubicación de anuncios" [VERIFICADO: https://support.google.com/adspolicy/answer/15936768†L24-L34].

**Actualización clave 14 abril 2025:** La prohibición aplica solo a **una sola ubicación de anuncios a la vez**. Google ahora puede mostrar 2 anuncios del mismo negocio si son ubicaciones distintas (ej. superior e inferior). [VERIFICADO: https://support.google.com/adspolicy/answer/16083544†L6-L17].

**¿Aplica a dos marcas/dominios del mismo dueño?** Sí, si Google las considera "misma empresa o negocio similar". El criterio es: mismo dueño + oferta similar + mismas keywords = riesgo de desaprobación/suspensión con aviso 7 días [VERIFICADO: https://support.google.com/adspolicy/answer/15936768†L11-L13]. Dominios distintos no te eximen.

**MCC:** Conviene **una sola MCC (Cuenta de administrador)** para ambas cuentas. [SUPUESTO: facilita ver colisión, aplicar etiquetas y negativas cruzadas]. No evita la política, pero te da visibilidad y te permite mostrar a Google que hay separación intencional. Dos MCC separadas aumenta riesgo de ser visto como intento de evadir. [VERIFICADO: estructura MCC es best practice - https://support.google.com/google-ads/answer/6139186].

## 3. Marca y negativas

**Negativas cruzadas - cómo hacerlo bien:**
- En UberTransfer (aeropuerto): agregar como negativas exactas todas las keywords que Aereostar puja en aeropuerto. Usar lista de negativas compartida en MCC: `Lista_AEROPUERTO_Aereostar`.
- En Aereostar: agregar como negativas: [corporativo, bodas, eventos, turismo, compartido, privado fuera santiago, ubertransfer].
- Regla: **una frase, un dueño; una marca por búsqueda** [SUPUESTO]. Implementar con concordancia negativa exacta + frase para evitar fuga.
- Marca propia: cada cuenta solo su marca exacta + variaciones. Aereostar NO puja "ubertransfer", UberTransfer NO puja "aereostar" salvo acuerdo escrito.

**Riesgo marca "Uber" en UberTransfer:**
- "Uber" es marca registrada notoria. Google restringe uso de marcas de terceros en anuncio si hay reclamo del titular [VERIFICADO: https://support.google.com/adspolicy/answer/6118†L5-L11]. Google NO restringe uso como keyword [VERIFICADO: https://support.google.com/adspolicy/answer/6118†L30-L33], pero sí en texto del anuncio.
- Riesgo: Uber puede reclamar y Google te obliga a quitar "Uber" del título/descripción. Peor: demanda extrajudicial en Chile.
- Cómo verificar: 1) Buscar en INAPI.cl si "UberTransfer" está registrada. 2) Probar crear anuncio con "UberTransfer" y ver si sale "Aprobado (limitado) por marca". 3) Revisar https://support.google.com/adspolicy/answer/6118 formulario de reclamo [VERIFICADO].
- Mitigación: usar en anuncios "Transfer privado aeropuerto" y dejar "UberTransfer" solo en URL y logo; registrar marca defensiva.

## 4. Medición separada

- **Google Ads:** conversiones separadas por cuenta, sin importación cruzada. Una conversión = formulario/whatsapp por dominio. Etiquetar en GA4 con `conversion_id` distinto.
- **GA4:** 2 propiedades separadas (o 1 con 2 flujos). NO usar medición multidominio cruzada si quieres saber qué marca rinde. Cada dominio con su Google Tag con `linker` desactivado para no mezclar. [SUPUESTO: costo cero, se hace en GA4 admin].
- **Dashboard:** Looker Studio gratuito con dos fuentes: Coste por cuenta + conversiones por dominio. Así evitas mezclar.
- Verificar llamadas: número distinto por marca (call tracking gratuito con forwarding de Google Ads).

## 5. Cómo decidir con pocos datos qué marca lleva aeropuerto

Diseño low-cost sin romper política:

- **No competir simultáneamente.** Test secuencial, no paralelo: Semana 1-2 Aereostar aeropuerto con presupuesto controlado ($4.600/día estimado [VERIFICADO: archivo]). Semana 3-4 pausar aeropuerto en Aereostar y activar solo UberTransfer aeropuerto con misma lista y mismo presupuesto.
- **Métricas (en orden):** 1) CPA consulta (costo / lead), 2) Tasa de conversión (lead/clic), 3) CPC y % impresiones perdidas por presupuesto, 4) Calidad página (tiempo en tarifas).
- **Criterio decisión:** gana la que tenga CPA 20% menor con mínimo 20 conversiones por periodo. Si empate (<10% diferencia), gana la que tenga mejor página (tarifas por horario más claras) [SUPUESTO: UberTransfer tiene tarifas por horario, potencial ventaja].
- Presupuesto: no necesitas más, solo reasignas el mismo.

## 6. Qué datos pedirle a Rafael (máx 6)

1. Acceso lectura a cuenta Aereostar: gasto real, conversiones, CTR oct 2025-hoy.
2. Margen y precio promedio por traslado aeropuerto vs corporativo/boda (para calcular CPA máximo).
3. Capacidad operativa real por marca (flota SUV/vans disponible por horario alta/baja).
4. Qué marca quiere priorizar a largo plazo y si hay plan de fusionar.
5. Número de teléfono y formulario distinto por marca (sí/no).
6. Autorización escrita para usar lista de negativas cruzadas y pausar rubros en Aereostar.

## 7. Qué NO hacer (corta)

- NO pujar mismas frases aeropuerto en ambas cuentas a la vez (violación ventaja desleal) [VERIFICADO: https://support.google.com/adspolicy/answer/15936768].
- NO crear campañas Máximo rendimiento / Smart sin aprobación (rompe regla dueño).
- NO usar "Uber" en títulos de anuncio hasta verificar reclamo de marca [VERIFICADO: https://support.google.com/adspolicy/answer/6118].
- NO mezclar GA4 y conversiones entre dominios.
- NO dividir lista aeropuerto en dos mitades permanentes (pierdes escala en nicho chico).
- NO crear nueva cuenta o dominio para evadir política.

## Nivel de confianza

- **Alta** en parte política: texto oficial de ventaja desleal y marcas está citado y vigente 2025 [VERIFICADO].
- **Media** en recomendación B+A: depende de datos reales de Aereostar que no tengo (gasto, CPA). Si Aereostar no convierte, invertir liderazgo tiene sentido.
- **Baja** en tema marca "Uber": depende de registro INAPI y de si Uber reclama en Chile, no verificable sin búsqueda legal.

## Fuentes

- Política Ventaja desleal (ex double serving): https://support.google.com/adspolicy/answer/15936768
- Actualización 14 abril 2025: https://support.google.com/adspolicy/answer/16083544?hl=es
- Política Marcas registradas: https://support.google.com/adspolicy/answer/6118
- MCC best practice: https://support.google.com/google-ads/answer/6139186
- Datos demanda y previsiones: archivo 01_CONSULTA.md entregado (170 frases, pujas $269-$907, 1.100 clics)
