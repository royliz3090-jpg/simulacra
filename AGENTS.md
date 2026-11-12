# SIMULACRA — memoria del proyecto (es-LATAM)

Traduccion de **SIMULACRA** (juego LibGDX/Java) al **espanol latinoamericano**
como idioma **independiente y seleccionable** en el selector nativo del juego
(que ya soporta `en-us` y `zh-cn`). **NO se reemplaza el ingles.**

- Repo: `github.com/royliz3090-jpg/simulacra`
- Rama de trabajo activa: **`feature/traduccion-es-latam-v2`**
- Estado detallado y procedimientos: **`docs/ESTADO_TRADUCCION.md`** (leer primero;
  contiene el historial completo de sesiones, comandos y evidencia).

## Regla de oro
El sandbox es temporal. **GitHub es la unica fuente persistente.** Hacer commit +
push con frecuencia (cada tarea funcional, nunca >15 min sin respaldar).
Un commit local NO es respaldo: el push remoto debe completarse.

## Artefactos clave
- `translations/es-LATAM/en-us.fs` — fuente de la traduccion (formato Kryo `.fs`).
- `translations/es-LATAM/fixes_*.json` — parches aplicados sobre la fuente.
- `dist/core.assets` — ZIP con 8 miembros (`en-us.fs` intacto + `es-latam.fs` nuevo).
- `dist/core.binary` — blob KCB1 con las clases Java parcheadas.
- `dist/es-latam.fs` — copia del `.fs` final (debe coincidir con el embebido).
- `tools/` — `blob_tool.py`, `fs_fix_keys.py`, `apply_fs_fixes.py`,
  `build_locale_fs.py`, `build_core_assets.py`, `verify_build.py`,
  `build_all.sh`, `build_test_binary.sh`.
- `patch/game27/` — clases Java parcheadas (selector de idioma en `gb/GBMainMenu.java`
  y `MainMenu.java`; overrides en `gbeslatam/`).

## Mecanica del idioma (critico)
- El idioma activo vive en las preferences de LibGDX bajo `STATE_LANGUAGE`,
  con valores de "prefijo de contenido": `en-us://`, `zh-cn://`, `es-latam://`.
- `game27.Globals.contentPrefix` guarda ese prefijo; `game27.Grid` lo usa.
- El selector nativo aparece SOLO en un primer arranque limpio (sin
  `STATE_LANGUAGE` y sin partida guardada). Ver `docs/ESTADO_TRADUCCION.md` §23.

## Pipeline (reproducible)
```bash
pip install pycryptodome
sudo apt-get install -y wine xvfb x11-utils xdotool imagemagick \
     tesseract-ocr tesseract-ocr-spa p7zip-full default-jdk-headless
7z x -y -o/tmp/gameext SIMULACRA.7z.001
python3 tools/blob_tool.py extract /tmp/gameext/core.binary /tmp/pyclasses
python3 -c "import zipfile;zipfile.ZipFile('/tmp/gameext/support.binary').extractall('/tmp/supportdir')"
ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_all.sh
python3 tools/verify_build.py            # -> TODO VALIDADO
```

## Trampas conocidas (no repetir errores)
1. **Prefijo de longitud Kryo.** Cada cadena `.fs` lleva 4 bytes big-endian de
   longitud. `fs_fix_keys.py` YA lo reescribe si cambia el tamano; si se escribe
   un `replace` propio, hay que hacerlo o se corrompe la cadena siguiente.
2. **Truncamientos (1033 reparados; cuerpo casi cerrado).** La traduccion base
   se aplico in-place respetando la longitud en bytes del ingles, dejando cientos
   de cadenas cortadas. Firma fiable: cadena ES de la MISMA longitud en bytes que
   la EN + relleno de espacios finales + termina en letra (sin puntuacion). Ficheros
   `translations/es-LATAM/fixes_truncados4..8.json`, `fixes_nombres_typos.json`,
   `fixes_localizacion.json`; se aplican en orden con `tools/apply_fs_fixes.py`.
   Detalle completo en `docs/ESTADO_TRADUCCION.md` §13.
   OJO: el `git config remote.origin.fetch` de este clon venia estrecho (solo
   `main`); corregido a `+refs/heads/*:refs/remotes/origin/*` para que
   `origin/feature/traduccion-es-latam-v2` no quede obsoleto. Comprobar el remoto
   real con `git ls-remote` o la API, no con `origin/<rama>` a ciegas.
3. **Wine sin `support.binary`** -> `ClassNotFoundException: DesktopLauncher`.
   El classpath necesita `support.binary` (ZIP) ademas de `core.binary`.
4. **No usar `--add`** al construir `core.assets` (duplica el miembro
   `es-latam.fs`); usar `--replace`.
5. **Apps internas.** Se desbloquean por la historia (`CONTEXT_APP_*`); el codigo
   de bloqueo lo fijan los `game27.triggers.Triggers$*` (`setCodeKeys`), NO es un
   codigo fijo. Su OCR requiere jugar el prologo.

## Verificacion
- Estatica: `python3 tools/verify_build.py` (28139 cadenas, 0 prefijos corruptos,
  bytecode valido, `GBESLATAM` presente).
- En juego (Wine): pantalla de bloqueo y home en espanol, 0 excepciones;
  selector de idioma end-to-end escribe `STATE_LANGUAGE=es-latam://`.
- Evidencia en `docs/evidencia/`.
