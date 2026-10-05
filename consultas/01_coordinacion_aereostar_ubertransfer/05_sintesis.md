# 05 · Síntesis — coordinación Aereostar ↔ UberTransfer (30-09-2026)

Fuentes leídas: `02_respuesta_chatgpt.md` (GPT-5.6 Sol), `gemini-code-1790795248980.md` (Gemini; debía llamarse `03_respuesta_gemini.md`) y `04-Respuesta-Meta.md` (Meta AI).
Las afirmaciones sobre políticas de Google se **contrastaron con las páginas oficiales** el 30-09-2026 (abajo).

## 1. Veredicto
**Las tres coinciden en lo esencial**, y la recomendación queda así:
1. **Regla: una frase, un dueño; una marca por búsqueda.** Nunca las mismas frases genéricas en las dos cuentas.
2. **Reparto provisional (A + B):** *Aereostar* lleva los genéricos de **aeropuerto** (ya tiene campaña desde oct-2025); *UberTransfer* lleva **su propia marca** y los rubros
   **corporativo, bodas/eventos, turismo, compartidos, privados y fuera de Santiago**. Es una hipótesis hasta ver los resultados reales de Aereostar.
3. **No publicar nada de UberTransfer todavía.** Primero auditar Aereostar (términos de búsqueda, costo, clics, conversiones de 3–6 meses).
4. **No hacer la prueba C** (partir la lista en dos mitades): mezcla intenciones distintas y con poco presupuesto no compara limpio.
5. **Medición separada:** una propiedad de GA4 y conversiones por dominio; misma definición de «lead válido» en ambas marcas.
6. **Cuentas:** mantener **una cuenta por marca** y, si se quiere, vincularlas a **una cuenta de administrador (MCC)**; es gratis y no borra historial.
7. **Marca «Uber»:** riesgo real pero acotado; comprobar el registro en Chile (INAPI) antes de usar «Uber» en los textos de los anuncios.

## 2. Dónde discrepan y cómo se resuelve
| Tema | ChatGPT | Gemini | Meta AI | Decisión |
|---|---|---|---|---|
| ¿Lanzar UberTransfer ya? | No, primero auditar | No, primero auditar | **Sí, días 4–7** (2 campañas + marca) | **No.** Coincide con 2 de 3 y con la regla del proyecto (nada sin aprobación del dueño). |
| Prueba con gasto | Solo con datos históricos; si hace falta, secuencial | **Activar campaña en Aereostar con ~$4.600/día por 14 días** | Secuencial: 2 semanas una marca, 2 semanas la otra | **Descartar la de Gemini** (gasto sin aprobación y sin necesidad: primero el historial). Si después hace falta comparar, **secuencial**, nunca simultánea. |
| Umbral para decidir | No fija número | No | «CPA 20 % menor y mínimo 20 conversiones» | El número de Meta es **arbitrario**; usarlo solo como punto de partida a validar con Rafael. Ojo: Google Trends del proyecto muestra **más demanda en enero–febrero**, lo que distorsiona una prueba secuencial. |
| Negativas | Por campaña y según mapa de intenciones; **no** una negativa global «aeropuerto» en UberTransfer | Negativas «transfer aeropuerto…» en UberTransfer y rubros en Aereostar | Lista compartida; **negativa exacta** de las 170 frases | Hacerlas **por campaña**. Una negativa *exacta* solo bloquea esa frase exacta; las variantes se cuelan. No bloquear «aeropuerto» a la campaña de marca de UberTransfer. |

## 3. Política de Google: lo verificado y lo no verificado
| Afirmación | Resultado |
|---|---|
| La política vigente se llama **«Unfair advantage»** (ventaja injusta) y prohíbe «intentar mostrar más de un anuncio de tu negocio, app o sitio en una misma ubicación de anuncio». | **Verificado** ([política](https://support.google.com/adspolicy/answer/15936768)). |
| Cada destino debe aportar **«valor distinto»** y se desaconsejan productos similares en sitios relacionados. | **Verificado** (misma página). |
| Google **avisa al menos 7 días antes** de suspender. | **Verificado** (misma página). |
| **Aclaración de abril de 2025:** la prohibición es por **«una sola ubicación de anuncio»**, no en toda la página. | **Verificado** ([actualización](https://support.google.com/adspolicy/answer/16083544)). Solo lo dijo Meta; es correcto. **Baja el riesgo, pero no lo elimina** si ambas marcas ofrecen lo mismo con las mismas frases. |
| «Desde 2012 se fusionó la doble publicación en Unfair advantage» (Meta). | **No verificado.** No lo uso. |
| Usar una marca **como palabra clave** no está restringido; **en el texto del anuncio** puede restringirse tras reclamo del titular, para competidores directos o si confunde. | **Verificado** ([marcas](https://support.google.com/adspolicy/answer/6118)). Lo citaron ChatGPT y Meta. |
| Vincular una cuenta a un **MCC** no borra ni modifica su historial; cada cuenta puede desvincularse. | **Verificado** ([cuenta de administrador](https://support.google.com/google-ads/answer/6139186)). |
| «El MCC ayuda a cumplir la política / dos MCC parecen evasión» (Gemini, Meta). | **No verificado:** la página oficial no dice eso. El MCC sirve para **visibilidad**, no como escudo. |
| GA4 separado por dominio e importación de conversiones con evento clave. | **No lo verifiqué yo**; es práctica estándar y ChatGPT citó páginas oficiales de Google. |

## 4. Fiabilidad de cada respuesta
- **ChatGPT — alta.** Citas correctas, separa [VERIFICADO] de [SUPUESTO], prudente (no inventa umbrales, avisa que la política cambia).
- **Meta AI — media.** Citas correctas y buen diseño de prueba, pero mezcla datos no verificados (2012, MCC) y propone lanzar campañas ya.
- **Gemini — baja/media.** Sin verificaciones; enlace oficial con dominio errado (`adspolicies` en vez de `adspolicy`), una palabra en polaco («pierwszym»), negativas poco claras
  (p. ej. «uber transfer corporativo» en Aereostar) y un plan con gasto; se declara «alta confianza» sin respaldo.

## 5. Plan final (sin crear campañas ni gastar)
1. **Rafael entrega** (o autoriza lectura de) el historial de Aereostar: términos de búsqueda, costo, clics, conversiones de los últimos 3–6 meses.
2. **Definir «lead válido»** (formulario, clic de WhatsApp, llamada, reserva) igual en ambas marcas y dejarlo medido por dominio.
3. **Mapa maestro «frase → marca»** en el panel (columna «Marca dueña» + filtro, sincronizada): todo lo de aeropuerto = Aereostar (provisional); marca y rubros = UberTransfer.
4. **Preparar, sin activar:** negativas cruzadas por campaña y las dos campañas de marca.
5. **Marca «Uber»:** consultar el registro de «UberTransfer» en INAPI y si hubo avisos de Google o del titular; hasta saberlo, cuidar el nombre en los textos de anuncios.
6. **Revisión con Rafael** cuando esté el historial: confirmar quién lleva el aeropuerto y, solo si hace falta, diseñar una prueba **secuencial** con su presupuesto.

## 6. Preguntas para Rafael (las 7 que más repiten las IAs)
1. Historial de Aereostar (3–6 meses) y quién lo administra / accesos.
2. Qué conversiones están medidas hoy y cuáles son clientes reales.
3. Margen o precio por traslado: aeropuerto vs corporativo vs bodas.
4. Presupuesto máximo mensual/diario por marca.
5. Situación legal del nombre «UberTransfer» (registro, avisos).
6. Teléfono/WhatsApp y formulario distintos por marca; tarifas en los tramos 18:00–19:30 y 06:00–07:30.
7. Flota real (capacidad) disponible por horario alta/baja.

## 7. Qué decide el dueño ahora
- ¿Agrego al panel la columna **«Marca dueña»** con filtro y dejo las negativas cruzadas en el Borrador?
- ¿Preparo la **consulta al registro INAPI** (búsqueda pública, gratis) para «UberTransfer»?
