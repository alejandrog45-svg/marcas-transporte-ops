# Más clics sin subir costos — Google Ads (UberTransfer y Aereostar)

Investigación del 10-10-2026. **Es solo una lista de propuestas: nada de esto se aplicó.** Las campañas solo se leen (regla del dueño); cada cambio lo decide y lo hace el dueño en Google Ads. Las cifras del proyecto son lecturas reales de la API (solo SELECT); lo de internet viene de fuentes citadas y la mayoría son blogs de agencias, no documentación oficial de Google (se marca cuál es cuál).

## Lo que muestran los datos propios (lectura del 09-10)
| | UberTransfer (203-550-4421) | Aereostar (548-530-8262) |
|---|---|---|
| Clics / impresiones | 65 / 1.125 | 41 / 706 |
| Costo | CLP 15.810 | CLP 16.008 |
| Impresiones perdidas por **presupuesto** | 62 % | 81 % |
| Impresiones perdidas por **ranking** | (ver panel) | 0 % |
| Cuota de impresiones en búsqueda | 30 % | 18,5 % |

Lectura: en ambas marcas el límite es el **presupuesto**, no la calidad del anuncio (Aereostar pierde 0 % por ranking). Ganar más clics con el mismo gasto = que cada peso rinda más: bajar el costo por clic y no gastar en búsquedas que no sirven. Además, de 8 llamadas desde anuncios de UberTransfer, 7 figuran perdidas (`docs/medicion_conversiones_plan.md`): conviene contestar antes de comprar más clics.

## Funciones de Google Ads que ayudan sin subir el presupuesto (todas = propuesta)
1. **Palabras negativas.** Revisar el informe de términos de búsqueda del panel (menú Rendimiento/Segmentos) y excluir lo que no sirve (empleo, gratis, bus, etc.). Evita pagar clics irrelevantes. *Fuentes de agencia.*
2. **Programación de anuncios y dispositivos.** El panel ya guarda el historial por hora y por dispositivo: se puede concentrar el gasto en las horas y dispositivos con más clics y bajar o pausar el resto. *Fuentes de agencia.*
3. **Límite de CPC máximo con «Maximizar clics».** La página oficial de Google explica que, sin tope, la puja se ajusta para conseguir todos los clics posibles dentro del presupuesto, y que un tope controla cuánto se paga por clic. Un tope razonable puede dar más clics por el mismo gasto, con riesgo de perder posición: probar de a poco. ([Google: Maximizar clics](https://support.google.com/google-ads/answer/6268626))
4. **Recursos del anuncio (sitelinks, textos destacados, llamada y ubicación).** Google recomienda al menos 4 sitelinks; llamada + ubicación sirven a negocios de servicio en móvil; los datos de ubicación salen del perfil de empresa de Google, que debe estar al día. Mejoran el CTR esperado, que baja el costo por clic (el efecto en cifras es afirmación de agencias, no verificado). ([Google: mejorar anuncios con recursos](https://business.google.com/uk/resources/articles/improve-search-ads-with-assets/), [ayuda Google](https://support.google.com/google-ads/answer/7507884?hl=en))
5. **Calidad del anuncio y de la página de destino.** Relevancia del texto, CTR esperado y experiencia de la página determinan el costo por clic de cada subasta. *Fuentes de agencia.* Aquí pesan los hallazgos de las auditorías técnicas: aereostar.cl sin meta description, títulos largos, home sin H1. ([ejemplo](https://lineardesign.com/blog/lower-cpc/))
6. **Perdidas por presupuesto: recortar desperdicio antes de agregar plata.** Quitar términos, horas, zonas o dispositivos que gastan sin dar clics útiles; si hay varias campañas, mover presupuesto a la que rinde más. ([guía sobre cuota de impresiones](https://relevantaudience.com/google-ads-en/google-ads-limited-by-budget))
7. **Medir lo que importa.** Sin conversiones reales (llamadas contestadas, WhatsApp), ninguna estrategia inteligente puede optimizar: seguir `docs/medicion_conversiones_plan.md` (pasos A–F; F cambia datos de conversión y necesita aprobación expresa).

## Qué NO se recomienda
- Subir el presupuesto o las pujas «para ver qué pasa».
- Campañas inteligentes o Máximo rendimiento sin datos de conversión (regla del proyecto: campaña de BÚSQUEDA).
- Aplicar las «recomendaciones» automáticas de Google sin revisarlas: algunas suben el gasto.

## Cómo seguir (una cosa a la vez, con aprobación)
1. Dueño: revisar el informe de términos y elegir negativas (el panel ya los clasifica por tipo).
2. Dueño: decidir si prueba un CPC máximo y cuál (el panel muestra el CPC medio real: Aereostar ≈ CLP 390–585 según el período).
3. Rafael: arreglar meta description, títulos y H1 de aereostar.cl (mejora el costo por clic a futuro).
4. Con 7–14 días de datos, comparar con el historial que el panel ya guarda.

*Fuentes consultadas (todas de terceros salvo las dos de Google indicadas):* [KlientBoost](https://klientboost.com/ppc/lower-cpc/), [Linear Design](https://lineardesign.com/blog/lower-cpc/), [Relevant Audience](https://relevantaudience.com/google-ads-en/google-ads-limited-by-budget), [Windsor.ai](https://windsor.ai/google-ads-impression-share-budget-lost-vs-rank-lost/), [Google Ads Help](https://support.google.com/google-ads/answer/6268626).
