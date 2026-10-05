# Centro de Comando (E:\CONOCIMIENTO DEL NEGOCIO) — lectura del 30-09-2026

**Alcance:** solo lectura. No se copió ni modificó nada; no se abrió ninguna credencial. 123 archivos, ~2 MB.

## Qué es
El hub del ecosistema **Ferretería Oviedo El Manzano**: conocimiento del negocio y del ERP (JustTime/JustWeb, SQL Server solo lectura), bot de WhatsApp en Render, paneles
(El Manzano, Bodegas Gestión, SQL/BI, Litueche, Las Cabras), Alianza Padel, `control-center/` (panel local con PIN para correr los pipelines, acceso solo por Tailscale),
cuadernos de Gemini, `SECURITY.md` y mapas de flujo.

## Hallazgo principal
**No registra UberTransfer ni Aereostar** (0 menciones). Este proyecto es independiente: no mezclar código, datos ni credenciales con el ecosistema. No hay nada que integrar al
`control-center` (aquí los flujos corren en GitHub Actions, con otras cuentas).

## Reglas del ecosistema que SÍ aplican aquí
- **Regla suprema de secretos:** nada que dé acceso (tokens, cuentas de servicio, claves) en archivos versionados, en lo publicado ni en documentos; usar placeholders (`[TOKEN-XXX]`, `[PASSWORD]`).
- **Checklist pre-git / pre-deploy** (`SECURITY.md` §3 y §4): adaptado como `tools/check_seguridad.py` + `tests/test_seguridad.py` (corre en cada prueba y en el CI).
- **Safe Change, Prevención:** declarar el alcance (TOCO / RAZÓN / NO-TOCO), no tocar zonas intocables, verificar después del cambio.
- **Una tarea a la vez**, sin pedirle al dueño que pegue credenciales; decisiones en vez de valores.
- Herramientas portátiles en E: (Python, Node, Git, Firebase CLI).

## Reglas del ecosistema que NO aplican aquí (evitar confusiones)
- «No proponer AES-256 para bodegas»: es de Bodegas Gestión. Aquí el cifrado del panel es deliberado y propio.
- «El panel admin se despliega solo con Firebase CLI local, nunca con GitHub Actions»: es de El Manzano (el workflow borraba datos). Aquí el deploy diario por GitHub Actions es deliberado y verificado.
- Reglas del bot, del catálogo por Firebase Hosting y de las bodegas del ERP.

## Lo incorporado al proyecto
`tools/check_seguridad.py` (tokens, claves privadas, archivos prohibidos, `.gitignore`, clave AES del panel ausente de lo versionado y lo publicado, lo publicado sin datos en claro) y su prueba.

## Pendiente (requiere OK del dueño)
- Registrar `ubertransfer-ops` en el hub (una entrada en el mapa/CLAUDE.md del hub y, si quiere, un cuaderno de Gemini). No se hizo: la autorización era solo de lectura.
- Observación para el dueño, no de este proyecto: el hub anota como pendiente **rotar un `GITHUB_TOKEN`** que quedó expuesto en texto plano en una sesión antigua del bot.
