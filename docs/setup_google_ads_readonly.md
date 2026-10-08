# Conector Google Ads — solo lectura

El panel de UberTransfer queda preparado para mostrar métricas reales de Google Ads sin editar campañas, anuncios, pujas ni presupuestos.

## Identidades separadas

| Marca | Cuenta | Campaña | Estado inicial |
|---|---:|---:|---|
| UberTransfer | `2035504421` | pendiente de confirmar | Pendiente de conexión API |
| Aereostar | `5485308262` | `24331409273` | Pausada |
| Amadigital | `3717064621` | no conectar | Solo referencia histórica |

Los archivos `data/google_ads_*.json` contienen únicamente configuración no secreta. Nunca deben contener tokens OAuth, refresh tokens, claves privadas ni credenciales.

## Flujo previsto

1. Un proceso externo de lectura consulta Google Ads API con OAuth autorizado.
2. El proceso escribe un resumen por marca y campaña en el contrato `googleAds`.
3. `tools/panel/build.py` valida la marca, el customer ID, los campaign IDs y el modo `read_only`.
4. El armado cifra esos datos junto con el resto del panel.
5. El `index` de UberTransfer muestra estado, cuenta, campañas, última sincronización y métricas disponibles.

El siguiente paso técnico es conectar la extracción OAuth/API. No se habilita desde el panel y no puede ejecutar operaciones de escritura.
