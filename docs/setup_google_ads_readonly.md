# Conector Google Ads — solo lectura

El panel de UberTransfer queda preparado para mostrar métricas reales de Google Ads sin editar campañas, anuncios, pujas ni presupuestos.

## Identidades separadas

| Marca | Cuenta | Campaña | Estado inicial |
|---|---:|---:|---|
| UberTransfer | `2035504421` | `24325669851` | Conectada en modo explorador, solo lectura |
| Aereostar | `5485308262` | `24331409273` | Pausada |
| Amadigital | `3717064621` | no conectar | Solo referencia histórica |

Los archivos `data/google_ads_*.json` contienen únicamente configuración no secreta. Nunca deben contener tokens OAuth, refresh tokens, claves privadas ni credenciales.

## Flujo activo

1. `.github/workflows/panel-diario.yml` consulta Google Ads API con OAuth autorizado.
2. `tools/panel/sync_google_ads.py` guarda solo datos reales de lectura: campañas, anuncios, grupos, términos de búsqueda, dispositivos, horas, regiones, conversiones e histórico diario.
3. El sincronizador conserva el catálogo de campañas y anuncios vistos para detectar cambios de nombre sin inventar historial.
4. `tools/panel/build.py` cifra esos datos junto con el resto del panel.
5. `docs/panel_keywords.html` y el sitio publicado muestran el resumen, estadísticas, gráfico, historial y desgloses.

El botón de consulta del sitio mide `ubertransfer.cl`; no contiene credenciales y no consulta Google Ads directamente. La extracción de Ads queda en el flujo seguro del servidor/GitHub para no exponer el refresh token en el navegador. No se habilitan operaciones de escritura.
