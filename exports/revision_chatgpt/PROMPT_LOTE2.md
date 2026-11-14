# Prompt para ChatGPT — LOTE 2 (cierre): confirmar nombres y claves internas

Copia el bloque de abajo en ChatGPT y adjunta (o pega) el contenido completo de
`exports/revision_chatgpt/LOTE2.md` (195 pares).

El objetivo de esta pasada NO es traducir en masa, sino **confirmar** que lo que
queda sin traducir son nombres propios / claves internas del juego que NO deben
tocarse, y detectar cualquier frase real que se haya escapado.

---

Eres revisor de localizacion de videojuegos (ingles -> espanol latinoamericano).
Te doy una lista de cadenas de SIMULACRA (thriller de terror interactivo
ambientado en un telefono: mensajes de chat, correos, subtitulos de voz, paginas
web ficticias e interfaz). Cada linea tiene:

```
- EN: <texto en ingles>
  ES: <traduccion actual>  [<motivo de alerta>]  (x<repeticiones>)
```

Las alertas son heuristicas automaticas, NO errores confirmados. En esta lista
hay MUCHOS falsos positivos: nombres de personajes, marcas, hashtags, rutas de
archivo, correos, fechas, colores hex, identificadores y claves internas del
juego que el codigo usa para localizar recursos.

## Tu tarea

Para CADA linea, decide si el texto es **texto visible que debe traducirse** o
**algo que debe quedarse tal cual**, y clasificalo en una de estas categorias:

1. `TRADUCIR` — es una frase visible y su `ES` esta mal, cortado o sin traducir.
   Propón la traduccion correcta en espanol latinoamericano natural.
2. `NOMBRE` — nombre propio de persona, marca, usuario, hashtag o lugar.
   Debe quedarse como esta.
3. `CLAVE` — clave interna / identificador que el juego usa en su logica
   (albumes de la galeria como `Camera`, `Chat Images`, `Voicemail`,
   `Recovered`, `Me`, `Spark`; rutas `*.web`; codigos de trigger
   `ACT1.foo()` / `spark.demon.*`; identificadores `__LINK0`).
   Traducirlos ROMPE el juego. Deben quedarse como estan.
4. `TECNICO` — fecha (`26 April 2017`), hora, color hex, numero o codigo.
   Se conserva tal cual (el parser lo exige en ingles).

## Reglas

- Espanol latinoamericano natural, tono coloquial del personaje. Nada literal.
- NO traduzcas: rutas de archivo, nombres propios, correos, hashtags ni codigo
  de triggers.
- CONSERVA exactamente: variables `#state:boot.name#`, enlaces `__LINK0`,
  etiquetas `[MAIL_BOLD] ... []`, saltos de linea `\n` y prefijos de URI
  (`corrupted://`, `photoroll://`, `vo://`, `graphic://`).
- Ante la duda de si algo es visible o es clave interna, marca `CLAVE` y
  explicalo en una linea. Es preferible no traducir una clave que romper el
  juego.
- No inventes cadenas nuevas. No cambies la clave `EN`.

## Formato de salida

Devuelve SOLO dos bloques:

**1) Las que SI hay que traducir** (si no hay ninguna, devuelve `[]`):

```json
[
  {"en": "texto en ingles exacto", "es": "traduccion corregida"}
]
```

**2) Confirmacion del resto**, agrupada por categoria:

```
CLAVE: Camera, Chat Images, Voicemail, Recovered, Me, Spark, ...
NOMBRE: Greg, Taylor, Anna, Ashley, Abby Shin, ...
TECNICO: 26 April 2017, 00cc33, ...
```

Al final, una linea: `RESUMEN: N a traducir, M nombres, K claves, J tecnicos`.

---

## Tras la respuesta de ChatGPT

Si el bloque (1) trae correcciones:

```bash
# 1. guardar el JSON devuelto como fixes_lote3.json
python3 tools/validate_fixes.py --fixes fixes_lote3.json \
  --out exports/validacion_lote3.json
python3 tools/apply_chatgpt_fixes.py work/chatgpt/en-us.fs \
  translations/es-LATAM/en-us.fs fixes_lote3.json work/chatgpt/en-us.src.new3
cp work/chatgpt/en-us.src.new3 translations/es-LATAM/en-us.fs
bash tools/rebuild_es.sh
python3 tools/verify_build.py && python3 tools/verify_es_latam_coverage.py
python3 tools/export_auditoria.py && python3 tools/export_revision.py
```

Si el bloque (1) es `[]`, la traduccion esta cerrada: solo falta la prueba en el
juego (Wine).
