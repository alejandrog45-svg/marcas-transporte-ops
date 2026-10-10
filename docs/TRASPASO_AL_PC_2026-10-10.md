# Volver al PC: cómo actualizar la carpeta local sin romper nada (10-10)

Fuente de verdad: GitHub `alejandrog45-svg/marcas-transporte-ops`, rama `main`. Todo lo hecho en la nube (Aereostar conectado, diseño, banner, fotos, IA por marca) está ahí y publicado. Se comprobó con un clon limpio: 89 pruebas OK y `python tools/panel/build.py` arma ambos paneles.

## 0. Qué carpeta usar (importante)
- **Vigente:** `W:\PROYECTOS CUENTA ALEJANDROG45\marcas-transporte-ops` (remoto `alejandrog45-svg`).
- **NO tocar con git:** `E:\ubertransfer-ops`. Es la copia vieja y su remoto es `oviedoem` (cuenta de la Ferretería). No hacer `pull` ni `push` ahí; queda solo como respaldo de lectura.
- Herramientas de `W:\...\herramientas-portables` (Python, Node, gh, Firebase), no las de `E:`. Firebase siempre con `--account alejandrog45@gmail.com`.

## 1. Antes de actualizar
1. Copiar la carpeta de W: completa a un respaldo (zip o carpeta con fecha).
2. `git status` y `git log origin/main..HEAD` (después de `git fetch origin`): si hay commits locales sin subir o archivos modificados, **no seguir**; revisar primero qué son.
3. Los dos archivos sin seguimiento del traspaso del 09-10 no se borran ni se suben.
4. Si `data/panel_data.enc.json` o `data/panel_data_aereostar.enc.json` salen modificados por un armado local viejo: `git checkout -- data/panel_data.enc.json data/panel_data_aereostar.enc.json` (la versión de GitHub es la buena).

## 2. Actualizar
```
git fetch origin
git checkout main
git pull --ff-only origin main
```
`--ff-only` falla si la historia local se desvió: en ese caso se avisa, no se fuerza.

## 3. Comprobar
- `python -m pytest -q` → 89 pruebas.
- `python tools/check_seguridad.py` → OK.
- `python tools/panel/build.py` con la clave del PC. Debe decir «se reutiliza … las entradas no cambiaron» y no modificar los `.enc.json` (si los modifica, no subirlos sin avisar).
- Abrir ambos paneles con la sesión del dueño: UberTransfer y `/aereostar/`, insignia «AG · v.11», verificaciones sin fallas.

## 4. Reglas para trabajar desde el PC
- **Publicar** = push a `main` + flujo `panel-diario.yml`. No hacer `firebase deploy` local salvo que se necesite, y solo después de actualizar: dos publicadores se pisan.
- Cada día el flujo programado sube un commit `data: auditoría diaria`. Antes de cada `push` local: `git pull --rebase origin main`.
- No fusionar la rama `ccr-8b4f70ce-5obz3r` (otra sesión; 16 commits hechos sobre una versión anterior; sus cambios ya están en `main` con otra forma). Sirve solo de referencia (p. ej. `tests/test_brand_isolation.py`).
- Campañas de Google Ads: solo lectura.
- Revocar al volver: la autorización de Supermetrics si se dio, accesos extra a la sesión de nube y cualquier clave pegada en un chat.

## 5. Automatización diaria (resumen)
Flujo `panel-diario.yml`, cron `30 5 * * *` UTC = 02:30 hora de Chile en verano (01:30 en invierno). GitHub retrasa los horarios programados (se vieron entre 4 y 6 horas), así que puede arrancar entre las 02:30 y las 08:00. Orden: auditoría de ubertransfer.cl → Google Ads UberTransfer (cuenta 203-550-4421) → Google Ads Aereostar (548-530-8262) → sugerencias por reglas (un documento de Firestore por marca) → IA Gemini UberTransfer → IA Gemini Aereostar → armar paneles → guardar datos en GitHub → publicar en Firebase. Datos, historial, sugerencias e IA van en archivos separados por marca.
