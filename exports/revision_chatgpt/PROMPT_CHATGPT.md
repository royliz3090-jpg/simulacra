# Prompt para ChatGPT - revision de traduccion es-LATAM de SIMULACRA

Copia el bloque de abajo en ChatGPT y adjunta (o pega) el contenido de
`UNICOS.md`. Devuelve las correcciones en el formato indicado para poder
aplicarlas con las herramientas de `tools/`.

---

Eres revisor de localizacion de videojuegos. Te doy una lista de cadenas de
texto del videojuego SIMULACRA en ingles (`EN`) y su traduccion actual a espanol
latinoamericano (`ES`). Tu tarea es **corregir y completar** la traduccion al
espanol latinoamericano.

Contexto del juego: thriller de terror interactivo ambientado en un telefono.
Los textos son mensajes de chat (Whatsup/Jabbr), correos, subtitulos de voz,
paginas web ficticias y textos de interfaz. Tono coloquial y natural.

Reglas estrictas:

1. Espanol latinoamericano natural. NO literal. Manten el tono del personaje.
2. NO traduzcas ni cambies: rutas de archivo, nombres propios (Greg, Anna,
   Taylor, Ashley, Murilo, Yolanda, Cassie, James, Toby...), correos
   electronicos, ni codigo de triggers (`ACT1.foo()`, `Triggers...`).
3. CONSERVA EXACTAMENTE estos marcadores si aparecen:
   - variables `#state:boot.name#`, `#...:...#`
   - enlaces `__LINK0`, `__LINK23`, ...
   - etiquetas `[MAIL_BOLD] ... []`, `[BOLD]`, `[]`
   - saltos de linea `\n`
   - prefijos `corrupted://`, `photoroll://`, `vo://`, `graphic://`
4. Si `problemas` incluye `relleno_espacios`, la traduccion actual puede estar
   cortada (lleva espacios finales de relleno). Reescribe la frase completa y
   correcta.
5. Si incluye `contenido_faltante`, traduce el contenido completo del ingles.
6. Si incluye `marcadores_distintos`, repon los marcadores que falten.
7. Si `ES` es igual a `EN` (`sin_traducir`), traduce la cadena.

Devuelve una tabla o una lista JSON con SOLO las cadenas que cambies:

```json
[
  {"en": "texto en ingles exacto", "es": "traduccion corregida"}
]
```

No incluyas las cadenas que ya esten correctas. No inventes cadenas nuevas.

---

## Tras la respuesta de ChatGPT

Guarda la lista en `fixes.json` y aplica las correcciones segun el tipo de
objeto (ver `docs/ESTADO_TRADUCCION.md`, seccion 24):

```bash
# objetos planos
python3 tools/apply_fs_fixes.py dist/core.assets fixes.json dist/core.assets
# objetos comprimidos
python3 tools/apply_blob_fixes.py ...
# reconstruir y validar
bash tools/rebuild_es.sh
python3 tools/validate_export.py
python3 tools/export_auditoria.py            # re-extraer y ver el nuevo estado
```

Repite `export_auditoria.py` -> `export_revision.py` -> ChatGPT -> aplicar, por
lotes, hasta que `sin_traducir` y `relleno_espacios` lleguen a cero.
