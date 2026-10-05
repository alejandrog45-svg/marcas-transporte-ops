# Panel de UberTransfer — cómo se arma

El panel es una sola página estática (sin servidor, sin claves). Se genera desde datos reales del repo.

```
python tools/panel/build.py
```

Escribe `docs/panel_keywords.html` (para abrir en local) y `site/index.html` + `site/version.json` (lo que se publica).
La primera vez ejecuta `npm install` dentro de esta carpeta (solo Tailwind, para compilar el CSS). Necesita Node.js.

## De dónde salen los datos
| Dato | Archivo |
|---|---|
| Frases, volúmenes y pujas | `data/keyword_planner_AAAAMMDD.csv` + `.meta.json` (fecha de exportación y cantidad de filas) |
| Previsión oficial de Google | `data/forecast_google.json` |
| Auditoría del sitio | `data/audit_latest.json` (la genera `python -m marcas_transporte_ops audit`) |
| Ideas de ChatGPT/Gemini | `tools/panel/ias.html` |

El armado se detiene si el CSV no tiene las filas que dice el `.meta.json` (consistencia).

## Actualizar datos
1. Nuevo CSV del Planificador → copiarlo a `data/` como `keyword_planner_AAAAMMDD.csv` y crear su `.meta.json`.
2. Nueva previsión → actualizar `data/forecast_google.json` (se lee de la pestaña Previsión; Google redondea).
3. `python tools/panel/build.py` y publicar (ver `CLAUDE.md`, sección de publicación).

## Dos paneles: UberTransfer y Aereostar
`python tools/panel/build.py` arma **dos** páginas desde la misma plantilla: `site/index.html` (UberTransfer) y `site/aereostar/index.html` (Aereostar, en `/aereostar/`). La de Aereostar se deriva con `brand_aereostar()` en `build.py` (nombre, sitio medido, favicon, lista de mejoras propia, teléfono PENDIENTE, sin auditoría ni ampliación).

- **Datos separados:** el navegador usa el prefijo `ae_` (`const KP`) y la nube el documento `panel/estado_aereostar` (UberTransfer: sin prefijo y `panel/estado`). Probado: marcar algo en uno no toca al otro.
- **Mismo login y misma clave:** un solo inicio de sesión sirve para ambos (mismo origen) y `panel/clave` descifra los dos (`data/panel_data.enc.json` y `data/panel_data_aereostar.enc.json`).
- **Botón de cambio** en el encabezado: «Panel Aereostar →» / «← Panel UberTransfer».
- **CSS:** Tailwind lee `.build/*.html` (las dos plantillas, que el armado escribe antes de compilar). El armado se detiene si el CSS sale chico (<20 KB). Lección: una vez GitHub publicó sin estilos porque faltaba ese archivo.
- **Sin auditoría de Aereostar todavía:** por eso su panel da 17/17 (las 2 verificaciones que dependen de la auditoría del sitio no aplican). Cuando exista `audit` de aereostar.cl se suman.

## Datos cifrados (acceso privado)
`site/index.html` (lo publicado) NO lleva las frases, la previsión ni las tendencias en claro: van cifradas con AES-256-GCM en `data/panel_data.enc.json` y el navegador las descifra solo tras iniciar sesión con Google, con una clave que vive en Firestore (`panel/clave`, legible solo por los correos de `firestore.rules`). `docs/panel_keywords.html` (local, ignorado por Git) sigue en claro.

- **Clave:** `E:\config\ubertransfer_panel_key.dpapi` (DPAPI, solo este PC/usuario) o la variable `PANEL_DATA_KEY`. Nunca en Git.
- **Sin clave (GitHub Actions):** el armado reutiliza `data/panel_data.enc.json` si las entradas no cambiaron; si cambiaron, se detiene y pide armar en el PC del dueño.
- **Cambiaron frases/previsión/tendencias:** armar en el PC del dueño (re-cifra y comprueba el descifrado), subir `data/panel_data.enc.json` y publicar.
- **Rotar la clave:** borrar `panel/clave` en la consola de Firestore, borrar el `.dpapi` y `data/panel_data.enc.json`, generar una clave nueva, armar y volver a crear `panel/clave` (las reglas solo permiten crearla una vez).
- El armado aborta si encuentra datos en claro en la versión publicada o si el cifrado altera el orden de las filas (rompería la huella SHA-256).

## Diseño
Tomado de Stitch (`docs/DESIGN_stitch.md`): tokens de color y tipografía en `tw.config.js`. Las fuentes e íconos se cargan de Google Fonts.
No se usaron los datos de ejemplo de la maqueta: todo lo que muestra el panel viene de los archivos de arriba.
