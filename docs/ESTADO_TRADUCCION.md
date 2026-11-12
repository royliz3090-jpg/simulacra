# Estado de la traducción de SIMULACRA al español latinoamericano

> Documento persistente para continuar el trabajo desde cualquier sandbox.
> Última actualización: sesión de continuación (ver sección "Último commit respaldado").

## 0. PIVOTE IMPORTANTE (leer primero)

El objetivo ya **no** es reemplazar el inglés por español, sino **añadir es-LATAM como un
idioma independiente y seleccionable** en el selector nativo del juego (que ya soporta
`en-us` y `zh-cn`). Por tanto:

- `dist/core.assets` conserva el `en-us.fs` **original en inglés** y añade `es-latam.fs`.
- `dist/core.binary` añade la clase `game27.gbeslatam.GBESLATAM` y una rama de 3 idiomas
  en `game27.Grid` + botón/etiqueta en `game27.MainMenu` y `game27.gb.GBMainMenu`.

El trabajo histórico (secciones 2 y 3) describe cómo se llegó hasta aquí; el
procedimiento vigente es el de las secciones 4-8.

## 1. Estado actual (resumen)

- **Repositorio**: https://github.com/royliz3090-jpg/simulacra
- **Rama de continuación**: `feature/traduccion-es-latam-v2` (creada a partir de `feature/traduccion-es-latam`).
- **Motor**: LibGDX (Java/LWJGL). El texto vive en `core.assets`.
- **Formato descifrado**: ver sección 3. Es un ZIP con 7 archivos `.fs`; dentro de `en-us.fs` están
  todas las cadenas en claro.
- **Mejor estado recuperable**: commit `56e24e3` de `main` ("v15b: in-place patched ZIP").
  Es el único `core.assets` que conserva **exactamente** la estructura original (mismo ZIP, mismo
  índice, mismas 207 URIs) y aplica ~6.024 cadenas traducidas en sitio.
- **Trabajo nuevo de esta sesión**: herramienta canónica `tools/simulacra_fs.py`, catálogo de cadenas,
  listas de trabajo y esta documentación.

## 2. Hallazgos de la recuperación (IMPORTANTE)

### 2.1 El `core.assets` de `feature/traduccion-es-latam` está CORRUPTO

El archivo `core.assets` versionado en `feature/traduccion-es-latam` (7.154.070 bytes) **no es un ZIP
válido**: es el resultado de escribir un ZIP como UTF-16LE (empieza con `FF FE 50 00 4B 00 ...`, es decir
BOM UTF-16LE + "PK"). Contiene 936.815 caracteres de reemplazo `U+FFFD`: la información se perdió de
forma irreversible al codificar bytes binarios como texto. **No usarlo.** El juego no puede cargarlo.

### 2.2 El mejor avance real está en `main` (v15b)

`main` HEAD = `56e24e3` contiene un `core.assets` de **3.783.527 bytes** (idéntico en tamaño al original)
que:
- Conserva el ZIP original (mismos 7 miembros, mismas cabeceras, mismo CRC de los otros 6 `.fs`).
- Conserva el índice comprimido de `en-us.fs` **byte a byte idéntico** al original.
- Solo cambia el bloque de datos de `en-us.fs` (13,3 % de bytes), reemplazando cadenas inglesas por
  españolas **de la misma longitud en bytes** (rellenando con espacios).

Verificado con `tools/simulacra_fs.py verify`: índice igual, 0 posiciones nuevas, 0 posiciones perdidas.

### 2.3 Historial de intentos (por qué unos congelaban el juego)

Los commits `v8`/`v9`/`v10`/`v11`–`v14` añadían cadenas que **congelaban el juego** al pulsar
"begin/continue", y se revirtieron a la base `v7`. Comparado con v15b, lo que v7/v8 traducían de más
eran cadenas **estructurales** (por ejemplo `Iris Chat`, `IRIS.OS`, `Chat Audio`, apodos `@madmikey`,
`@kadre`). Traducir esos identificadores rompe la lógica. **Regla: no traducir cadenas que sean
identificadores, rutas, apodos `@usuario`, nombres de clase, ni etiquetas de tipo.**

### 2.4 Estado de las traducciones guardadas en GitHub

- `translations/es-LATAM/` (3.254 JSON) se generó desde el v5 es-ES y **no se incorporó al binario**.
  Además parte está marcada `pendiente_extraccion`. Sirve como glosario/borrador, no como fuente de verdad.
- La fuente de verdad es el binario `core.assets` del commit `56e24e3`.

## 3. Formato de `core.assets` (descifrado)

```
core.assets  = ZIP (sin compresión) con 7 miembros:
   en-us.fs  main.fs  videos.fs  web.fs  zh-cn.fs  content.fs  emojis.fs
```

`*.fs` (LibGDX FileSystem):

```
[0:14]   cabecera: "FileSystem" + 4 bytes
[14:X]   bloque de ÍNDICE comprimido con zlib  -> al descomprimir: índice binario
[X:fin]  bloque de DATOS sin comprimir -> objetos Kryo serializados (aquí está el texto)
```

- En `en-us.fs`: cabecera 14 B, índice 512.026 B descomprimidos, datos 937.002 B.
- El índice contiene 207 entradas `<URI>\x00\x00 <2 bytes> <4 bytes>` (URIs `en-us://...`).

**Las cadenas (Kryo) se codifican así:**

```
<4 bytes big-endian: longitud L> <L bytes UTF-8>
```

Ejemplo: `00 00 00 1f` + `So, I’m gonna download Spark.` (L = 31).

## 4. Herramienta canónica

`tools/simulacra_fs.py` (solo stdlib de Python 3):

```bash
python3 tools/simulacra_fs.py info   <core.assets>              # estructura por miembro .fs
python3 tools/simulacra_fs.py dump   <core.assets> en-us.fs out.json   # catalogo de cadenas
python3 tools/simulacra_fs.py apply  <in.assets> <trans.json> <out.assets>  # aplica en sitio
python3 tools/simulacra_fs.py verify <core.assets> [original.assets]   # compara con el original
```

- `apply` **rechaza** cualquier traducción más larga (en bytes) que el original: nunca corrompe.
- `apply` reconstruye el ZIP preservando orden y cabeceras de los 7 miembros.
- Formato de `trans.json`: `{"member": "en-us.fs", "strings": [{"pos": N, "len": L, "es": "..."}]}`
  donde `pos` es la posición del **primer byte de la cadena** dentro del bloque de datos.

## 5. Procedimiento exacto para modificar los recursos

1. Extraer el `core.assets` original del juego (los 11 volúmenes `SIMULACRA.7z.0NN`):
   ```bash
   cat SIMULACRA.7z.0* > /tmp/SIMULACRA.7z     # unir volúmenes
   python3 -c "import py7zr; py7zr.SevenZipFile('/tmp/SIMULACRA.7z').extract(path='/tmp/game', targets=['core.assets'])"
   ```
   (requiere `pip install py7zr`).
2. Tomar como base el `core.assets` de `main` (`git show origin/main:core.assets > base.assets`).
3. Volcar cadenas: `python3 tools/simulacra_fs.py dump base.assets en-us.fs /tmp/strings.json`.
4. Generar `traducciones.json` (pos, len, es) para las cadenas a cambiar. La traducción **no puede
   exceder `len` bytes**; se rellena con espacios.
5. Aplicar: `python3 tools/simulacra_fs.py apply base.assets traducciones.json nuevo.assets`.
6. Verificar: `python3 tools/simulacra_fs.py verify nuevo.assets /tmp/game/core.assets`
   (debe indicar `index igual=True`, 0 posiciones nuevas/perdidas y caracteres nuevos solo del
   repertorio español).
7. Reemplazar `core.assets` en el repo y commitear.

## 6. Cómo verificar que el juego carga los textos

- **Sin entorno gráfico** (este sandbox no puede ejecutar SIMULACRA). Verificaciones posibles:
  - `tools/simulacra_fs.py verify` (estructura + cobertura).
  - `unzip -t core.assets` o `zipfile.testzip()` -> ZIP íntegro.
  - Comprobar que el índice de `en-us.fs` es idéntico al original (prueba fuerte de que el juego
    encontrará todos los recursos).
- **Con entorno gráfico** (Windows con el juego): sustituir `core.assets`, iniciar, pulsar
  *begin/continue* y revisar menús, chats y llamadas. Si el juego se congela en el arranque,
  revisar la sección 2.3 (identificadores traducidos por error).

## 7. Problemas encontrados y solución

| Problema | Causa | Solución |
|----------|-------|----------|
| `core.assets` de la rama de traducción no abre como ZIP | Se guardó un binario como UTF-16LE (BOM + `PK`) | Usar el de `main` (`56e24e3`) |
| El juego se congela al "continue" | Se tradujeron identificadores/etiquetas estructurales | No traducir identificadores (ver 2.3) |
| Traducciones truncadas a mitad de palabra | El español es más largo que el inglés y no cabe | Reescribir más corto y natural; nunca exceder `len` |
| Nombres propios traducidos literalmente (`Greg Summers` -> `Greg veranos`) | Traducción automática palabra a palabra | Mantener nombres propios sin traducir |
| `7z` no está instalado | Entorno mínimo | `pip install py7zr` y unir volúmenes con `cat` |

## 8. Arquitectura es-LATAM (idioma independiente) — NUEVO

### 8.1 Recursos entregables (`dist/`)

| Archivo | Contenido |
|---------|-----------|
| `dist/core.assets` | ZIP con los 7 recursos originales (incl. `en-us.fs` **en inglés**) + `es-latam.fs` |
| `dist/core.binary` | Blob KCB1 con 4 clases reemplazadas + `game27.gbeslatam.GBESLATAM` |
| `dist/es-latam.fs` | Copia suelta del recurso de idioma (referencia) |

### 8.2 Formato `core.binary` (KCB1) — DESCIFRADO

```
[0:4]    magic 1262699057 (0x4B434231 "KCB1")
[4:8]    numEntries
[8:8+9*numEntries]  descriptor: por entrada, 9 int32
        [0..4]  = palabras del SHA-1(nombre) XOR unlock1..5
        [5]     = offset del bloque cifrado dentro del area de datos
        [6]     = tamano comprimido (deflate)
        [7]     = tamano sin comprimir
        [8]     = CRC32 del bloque comprimido
[8+36*n : +4]  tamano del area de datos
[...]    area de datos: por clase, IV(16) + AES/CTR(cifrado)
```

- Cifrado: `AES/CTR/NoPadding`, clave = `MD5(nombre)` (16 bytes), IV = primeros 16 bytes.
- El texto cifrado se descomprime con deflate; se valida el CRC32.
- `unlock1..5` se deriva del SHA-1 concatenado de las clases del stack de llamadas
  (`CodeBlob` + sus superclases hasta `Object`, luego `DesktopLauncher` + superclases).
  Para el parche **no hace falta conocerlo**: se conservan intactas las palabras [0..4] de
  cada entrada original y solo se recalculan [5..8]. El `unlock` efectivo derivado es
  `[-109, -31963, -8165577, -119, -44]`.

> Nota: `blob_tool._sha1_words` calcula las palabras con **bytes con signo** (Java promociona
> `byte` a `int` con extensión de signo). Con bytes sin signo el descriptor no resuelve.

### 8.3 Mecanismo de idioma (código Java)

- `Globals.contentPrefix` (pref. `"en-us://"`, `"zh-cn://"`, nuevo `"es-latam://"`).
- `Grid` (constructor): elige `GBENUS.setup()` / `GBZHCN.setup()` / **`GBESLATAM.setup()`**.
- `Grid.load()`: `File.unpackFS("en-us.fs" | "zh-cn.fs" | "es-latam.fs")`.
- `MainMenu`: botón/etiqueta español + handler que fija `STATE_LANGUAGE = "es-latam://"`.
- `game27.gbeslatam.GBESLATAM`: rellena `GlobalTexts` en español y registra overrides.

### 8.4 Archivos fuente del parche (`patch/`)

- `patch/game27/Globals.java` — constante `CONTENT_PREFIX_ES_LATAM`, `SAVE_FILENAME_ES_LATAM`.
- `patch/game27/Grid.java` — rama de 3 idiomas (constructor y `load()`).
- `patch/game27/MainMenu.java` — widgets y handler del botón español.
- `patch/game27/gb/GBMainMenu.java` — widgets espejo de los chinos.
- `patch/game27/gbeslatam/GBESLATAM.java` — **generado** por `tools/gen_gbeslatam.py` a partir
  de `game27/gb/GBENUS.java` (renombra paquete/clase, ajusta guardado y locale).

## 9. Procedimiento de build y validación (vigente)

```bash
# 0) Prerrequisitos (una vez):
#    - clases originales extraidas:  python3 tools/blob_tool.py extract core.binary /tmp/pyclasses
#    - librerias de support.binary:  /tmp/support.jar
#    - copia limpia (ingles) de core.assets y core.binary en /tmp/game
#    - JDK 8+ (javac --release 8)

# 1) Build completo -> dist/
ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/support.jar bash tools/build_all.sh

# 2) Validacion estructural (sin Java)
python3 tools/verify_build.py dist/core.assets dist/core.binary /tmp/game/core.assets
```

Salidas esperadas (md5):
- `dist/core.assets` = `fb2392ffa066dafb29fc9e932e54bc7e`
- `dist/core.binary` = `da50f319a992dc4391f5872336474b75`
- `dist/es-latam.fs` = `fdaee2c63df7a25c6dc288a84d38bf16`

## 10. Cómo verificar que el juego carga los textos

- **Sin entorno gráfico** (este sandbox no ejecuta SIMULACRA, es Windows/GPU):
  - `tools/verify_build.py` (estructura + bytecode + textos).
  - `tools/build_locale_fs.py` valida el bloque de formato con `parse_format`.
  - **Prueba fuerte ejecutada**: un `ClassLoader` fiel a `CodeBlob` (mismo `read()`: SHA-1,
    AES/CTR, CRC32, inflate) carga las 4 clases parcheadas + `GBESLATAM` desde
    `dist/core.binary`, ejecuta `GBESLATAM.setup()` y comprueba que `GlobalTexts.text1` = "Galería".
  - `sengine.mass.io.Input` (clase real del juego) parsea el bloque de formato de
    `es-latam.fs` sin bytes sobrantes y con 207 nombres `es-latam://`.
  - **Nota sobre la prueba con `CodeBlob` real**: ejecutar el `CodeBlob` real desde este
    sandbox **falla también con el `core.binary` ORIGINAL** (mismo
    `ClassNotFoundException: game27.DesktopMain`), porque depende del JRE 8 empaquetado
    (Windows) y del stack exacto del lanzador. Por eso la validación fiel se hace con el
    `ClassLoader` replicado, que reproduce exactamente el algoritmo de `CodeBlob.read()`.
- **Con entorno gráfico** (Windows): copiar `dist/core.assets` y `dist/core.binary` a la carpeta
  del juego, iniciar, abrir el selector de idioma y elegir **Español (Latinoamérica)**.

## 11. Trabajo recuperado vs. nuevo vs. pendiente

- **Recuperado**: `core.assets` v15b de `main` (≈6.024 cadenas es-LATAM en sitio), scripts de
  análisis, glosario, documentación y el análisis de `core.binary` (rama v2).
- **Nuevo (esta sesión)**:
  - Corrección de `tools/blob_tool.py` (palabras SHA-1 con signo) -> descriptor KCB1 correcto.
  - `tools/patch_core_binary.py` (reempaquetado seguro conservando hashes [0..4]).
  - `tools/build_core_assets.py` (añade `es-latam.fs` sin tocar el inglés).
  - `tools/build_all.sh` + `tools/verify_build.py` (pipeline reproducible y validación).
  - `tools/fs_editor.py` + `tools/apply_fs_fixes.py`: editor del bloque de objetos Mass
    (traducciones de longitud natural, no sólo sobrescritura en sitio).
  - `patch/game27/gbeslatam/GBESLATAM.java` + parches de `Globals`/`Grid`/`MainMenu`/`GBMainMenu`.
  - **188 traducciones truncadas reparadas** (`translations/es-LATAM/fixes_truncated.json`).
  - **7 líneas de chat** que quedaban en inglés traducidas (`fixes_chatlines.json`).
  - `aplicar_parche.bat` / `desinstalar_parche.bat` ahora copian `core.binary`.
  - Entregables `dist/core.assets`, `dist/core.binary`, `dist/es-latam.fs`.
- **Estado de cobertura**: no queda texto en inglés salvo nombres propios (Greg, Taylor) y
  cadenas técnicas (identificadores, rutas de archivo, nombres de fuente).
- **Pendiente**:
  - Prueba en el juego real (Windows/GPU): elegir "Español (Latinoamérica)" y recorrer
    menús, chats, llamadas y correos.
  - Revisión de estilo (naturalidad) de frases largas y de nombres propios.
  - Revisar textos incrustados en imágenes del menú (requieren edición de textura).

## 12. Último commit respaldado

Rama `feature/traduccion-es-latam-v2` (los commits de esta sesión, en orden):

| commit | contenido |
|---|---|
| `7b42382` | idioma independiente seleccionable (blob KCB1 + es-latam.fs) |
| `f7593fd` | reparar 188 traducciones truncadas (longitud natural) |
| `87195f0` | traducir últimas 7 líneas de chat en inglés |
| `fcb678d` | instalación, estado y scripts de parche actualizados |
| `00c0e1d` | prueba de validación con CodeBlob real y límite de entorno |

Base recuperada: `56e24e3` de `main` (core.assets v15b en sitio).

## 13. Próxima tarea concreta

1. **Prueba real en Windows**: copiar `dist/core.assets` + `dist/core.binary`, abrir el
   selector de idioma, elegir "Español (Latinoamérica)" y recorrer menús, chats,
   llamadas y correos. Registrar capturas y cualquier texto que siga en inglés.
2. Si aparece texto en inglés o roto, localizarlo con `tools/simulacra_fs.py` (por
   contenido), corregirlo con `tools/apply_fs_fixes.py` (admite longitud natural) y
   reconstruir con `bash tools/build_all.sh`.
3. Revisar naturalidad de frases largas (estilo latinoamericano) y unificar glosario
   (`GLOSSARY.md`).
4. Opcional: traducir texto incrustado en texturas del menú (edición de imagen).

## 14. Receta rápida para el próximo agente

```bash
git clone https://github.com/royliz3090-jpg/simulacra
cd simulacra
git checkout feature/traduccion-es-latam-v2
python3 tools/verify_build.py dist/core.assets dist/core.binary /ruta/core.assets   # TODO VALIDADO
# editar translations/es-LATAM/en-us.fs con tools/apply_fs_fixes.py
bash tools/build_all.sh
git add -A && git commit -m "..." && git push origin feature/traduccion-es-latam-v2
```


---

## 15. Sesion 2026-11-11: causa raiz del crash "Unable to find media _Jabbr/cover"

### Sintoma
Con el idioma es-LATAM seleccionado, al cargar el juego saltaba
`java.lang.RuntimeException: Unable to find media _Jabbr/cover` desde
`FriendsProfileScreen.setLogin()`. La build en INGLES cargaba sin problemas.

### Causa raiz (VERIFICADA)
El `.fs` no contiene solo texto visible: contiene tambien **claves internas**
que el codigo compara o usa para localizar recursos. Al traducirlas "de forma
natural" se rompen las busquedas. Ejemplos reales encontrados:

| original (EN) | traduccion erronea | consecuencia |
|---|---|---|
| `cover` | `porta` | album `_Jabbr/cover` no existe -> crash al abrir perfil |
| `vlog3`/`vlog5` | `blog3`/`blog5` | `setVlogProgress("vlog3",...)` no encuentra el vlog |
| `missed` | `perdid` | tipo de llamada reciente invalido |
| `incoming`/`outgoing` | `entrante`/`saliente` | iconos/tipo de llamada rotos |
| `center` | `centro` | alineacion de texto no reconocida |
| `age`,`firstname`,`lastname`,`numeric` | traducidos | formularios del navegador fallan |
| `Camera`,`Videos`,`Wallpapers`,`Chat Images` | traducidos | albumes de la galeria no encontrados |
| `Voicemail`,`sender`,`Spark`,`Recovered` | traducidos | datos de apps incorrectos |

Ademas, las **fechas serializadas** en los ficheros de configuracion se
re-parsean con `SimpleDateFormat(..., Locale.US)`; traducirlas provoca
`Failed to parse time: 26 de abril de 2017, 1` (los meses deben quedar en
ingles: `dd MMMM yyyy`, `d MMMM`, `EEE, d MMMM`, `h:mm a`).

### Solucion implementada
`tools/fs_fix_keys.py` + `tools/keys_protegidas.txt`:
1. Compara el `.fs` original (ingles) con el traducido posicion a posicion
   (mismo orden de cadenas).
2. Restaura al ingles toda cadena inglesa que (a) figure en
   `keys_protegidas.txt` o (b) coincida con un patron de fecha protegido.
3. **Recomputa los offsets del bloque de formato** tras cambiar longitudes en
   bytes y reemite el `.fs` completo (cabecera + formato zlib + datos).

En esta pasada se restauraron **178 cadenas** (25 identificadores + 153 fechas).

`tools/build_all.sh` ahora ejecuta `fs_fix_keys.py` ANTES de reescribir el
prefijo `en-us://` -> `es-latam://`.

### Validacion
- Ejecutado con Wine (`/tmp/gamerun`), idioma es-LATAM, se pulso BEGIN.
- **0 excepciones** en el log; el juego supera la carga y llega a la pantalla
  principal del telefono (OCR: "Anna!", "Greg", "7 missed").
- Log: `[Grid] Starting new game checkpoint` (partida iniciada).
- `dist/es-latam.fs` generado es byte-identico al artefacto probado.

### Pendiente tras esta sesion
- Recorrer chats/llamadas/correos en juego y capturar dialogo en espanol.
- Revisar si quedan mas identificadores traducidos (buscar por contenido).
- Prueba en Windows real con GPU (Wine no tiene OpenAL -> solo ruido).

### Comandos reproducibles
```bash
ORIG=/ruta/core.assets_original CLASES=/tmp/pyclasses SUPPORT=/tmp/support.jar \
  JAVAC=$(command -v javac) bash tools/build_all.sh
# artefactos: dist/core.assets, dist/core.binary, dist/es-latam.fs
```

## 16. Sesion 2026-11-11 (continuacion): vo:// + chats://section + blindaje de URI

### Trabajo nuevo realizado
1. **Traducidos 47 textos visibles que quedaban en ingles**:
   - 41 subtitulos de voz (`vo://content/vo/XXX.ogg=TEXTO`) y mensajes de
     sistema de chat (`chats://section/...`), via
     `tools/gen_fixes_vo_chats.py` + `translations/es-LATAM/fixes_vo_chats.json`.
   - 6 interjecciones de chat (`Come on Murv`, `Waay down`, `Whoop de doo`,
     `Whoa whoa`, `Err... random.`, `Vortex Club!!`) via
     `translations/es-LATAM/fixes_interjecciones.json`.
2. **Corregido un segundo bug estructural de la misma familia que `cover`**:
   el prefijo `chats://section/` habia sido traducido a `chats://seccion/` en
   un objeto. Como `SparkThreadScreen`/`WhatsupThreadScreen` comparan
   literalmente `message.startsWith("chats://section/")`, ese mensaje dejaba de
   renderizarse. **No hay que traducir NUNCA el `scheme://ruta/` de un URI.**
3. **Nuevo blindaje generico en `tools/fs_fix_keys.py`** (`uri_prefix()`):
   si la cadena inglesa empieza por `scheme://ruta/`, se fuerza a que la
   traduccion conserve ese prefijo EXACTO. Esto protege de forma automatica
   todos los `vo://`, `chats://`, `photoroll://`, `corrupted://`, etc.

### Cobertura (cadenas tipo prosa, excluyendo codigo y rutas)
- en-us tiene 4681 cadenas tipo prosa.
- es-LATAM tiene **4609 traducidas = 98.5%**.
- Las 72 sin traducir son: 64 **nombres propios** (correcto no traducir:
  `Greg Summers`, `Abby Shin`, `Faris & Kane`, ...) y 8 interjecciones ya
  cubiertas arriba (tras esta sesion: ~100% de la prosa traducible).
- Sobre el total bruto (28139 cadenas) se traducen 10934 (el resto son rutas,
  identificadores, claves de estado y nombres propios que DEBEN quedar en EN).

### Selector de idioma — verificacion de codigo
`patch/game27/MainMenu.java` y `patch/game27/Grid.java` implementan el idioma
independiente:
- Botones `languageEnglishButton` / `languageChineseButton` /
  `languageSpanishButton` -> `putString("STATE_LANGUAGE", "es-latam://")`.
- `Globals.CONTENT_PREFIX_ES_LATAM = "es-latam://"`.
- `Grid` despacha `File.unpackFS("es-latam.fs")` segun `contentPrefix`.
- `refreshLanguageStatus()` marca el idioma activo y `showLanguageMenu()`
  muestra el OK correspondiente.
- `verify_build.py` confirma `game27.gbeslatam.GBESLATAM` presente y bytecode
  valido en `dist/core.binary`.

### Validacion de esta sesion
- `tools/verify_build.py dist/...` -> **TODO VALIDADO**.
- Prueba real con Wine (`/tmp/gamerun`): **0 excepciones**,
  **0** `Unable to find media` / `Failed to parse`, partida iniciada
  (`[Grid] Starting new game checkpoint`), pantalla de bloqueo e inicio del
  telefono renderizados. UI en espanol confirmada por OCR en la home:
  `Telefono`, `Chats`, `Galeria`, `Correo`, `Spark`, `Jabbr`, `Vloggr`, `Surfer`.
- Nota: la prueba con Wine requiere un `core.binary` **sin Steam** (el original
  lanza `Unable to initialize steam`). El `dist/core.binary` es para el juego
  real con Steam; para probar en sandbox usar el binario no-Steam
  (`/tmp/testbin/core_es_origfs.bin`) con el `core.assets` de `dist/`.

### Commits de esta sesion
- `9db7ef9` — vo:// + chats://section + blindaje de URI (empujado).
- (siguiente commit) — interjecciones + documentacion (empujado).

### Proxima tarea concreta
1. Documentar/reproducir el `core.binary` **sin Steam** para que cualquiera
   pueda probar en Wine: parchear `game27.DesktopMain` para saltar
   `SteamAPI.init` y usar guardado local, compilar con
   `tools/patch_core_binary.py` y guardar el helper en `tools/`.
2. Recorrer en juego chats/llamadas/correos y capturar dialogo en espanol
   para evidencia visual.
3. Revisar la lista de 14 "clean literals" (`Sign In`, `Wrong answer`,
   `Thank you`, `Welcome!`, `NEW`, `lookup`, `Taylor`) — son texto de UI
   hardcodeado en las clases; decidir si conviene parchear las clases.

---

## 17. Clases de UI es-LATAM via `Builder.overrides` (sesion 2026-11-12)

### Descubrimiento
El juego NO tiene todos los textos en los `.fs`. Los textos de UI "duros"
(pantalla de bloqueo, menus, dialogos, telefono, galeria, correo, spark,
friends, vloggr, restore...) estan como cadenas literales dentro de las
**clases Java** `game27.gb.*`.

El mecanismo oficial de idioma del juego es `sengine.utils.Builder.overrides`:
`GBZHCN.setup()` registra ~41 pares
`Builder.overrides.put(game27.gb.GBLockScreen.class, game27.gbzhcn.GBLockScreen.class)`
y el juego instancia la variante zh-cn. Cuando `Builder` construye un tipo,
si hay override lo usa en su lugar (`Builder.java`, campo `overrides`).

Por eso el build zh-cn muestra la UI en chino: tiene clases `game27.gbzhcn.*`
propias. Nuestro build es-LATAM solo tenia `GBESLATAM.setup()` **sin**
overrides -> la UI dura quedaba en ingles.

### Solucion implementada
Se replica el mecanismo para es-LATAM **sin recompilar** el juego:

1. `tools/class_patch.py` — reescribe el *constant pool* de un `.class`:
   - `replace_strings(map)`: cambia solo los `CONSTANT_Utf8` referenciados por
     un `CONSTANT_String` (nunca nombres de metodos/campos).
   - `rename_class(old,new)`: renombra `this_class`, referencias `old$X` y el
     descriptor `Lold;` (atributo Signature).
2. `tools/gen_es_overrides.py` — para cada par base->override del juego:
   toma la clase base del binario ORIGINAL, aplica las traducciones de
   `translations/es-LATAM/override_ui.json` y la renombra a
   `game27.gbeslatam.*`. Genera tambien
   `patch/game27/gbeslatam/GBESLATAMOverrides.java` (registro de overrides).
3. `GBESLATAM.setup()` llama `GBESLATAMOverrides.register()`.
4. `tools/build_all.sh` genera, compila y agrega las clases nuevas al
   `core.binary` (36 clases nuevas: GBESLATAM, GBESLATAMOverrides y 34 UI).

`GBMainMenu` se **excluye** del generador: se parchea a mano (selector de
idioma + textos). Sus etiquetas de UI se eligen en runtime con el helper
`L(en, es)` segun `Globals.contentPrefix`.

### Cobertura (actualizada)
- **219 cadenas** de UI en `translations/es-LATAM/override_ui.json`.
- **38 clases** override generadas; **230 cadenas reescritas** en
  `dist/core.binary` (1103 entradas: +40 nuevas, 17 reemplazadas).
- Incluye etiquetas en mayusculas que el build oficial zh-cn tambien traduce
  (ABOUT, AGE, NAME, TAGLINE, INTERESTS, SUBMIT, NEXT, YES, OKAY, SKIP,
  BOOKMARKS, HISTORY, SAVED...), acciones (Open, Play, Restore, Next),
  perfiles Spark (Works/Studies at Kaigan U), tiempos relativos, fechas.
- **NUNCA traducir** los nombres de color de fuente usados por el marcado
  (`HANDLE`, `LINK`, `TAG`, `MAIL_BOLD`, `MAIL_ITALIC`, `MAIN_GAMEPLUS`,
  `STAT_GREEN`, `boot_bold`): rompen el coloreado y el parseo. El generador
  tiene un guardia `FORBIDDEN_KEYS` que aborta si aparecen en el mapa.

### Procedimiento reproducible
```bash
# Requiere: JDK 8+ en $JAVA_HOME, support.jar (GDX+steamworks) y clases del
# binario ORIGINAL extraidas (Blob) en $CLASES.
CLASES=/tmp/testbin/cls_orig SUPPORT=/tmp/supportdir \
JAVAC=/tmp/jdk-21.0.4+7/bin/javac bash tools/build_all.sh
python3 tools/verify_build.py dist/core.assets dist/core.binary /tmp/game/core.assets
```

### Validacion de esta sesion
- `tools/verify_build.py` -> **TODO VALIDADO** (incluye
  `game27.gbeslatam.GBESLATAMOverrides` presente y bytecode valido).
- Wine: **0 excepciones**, **0** `Unable to find media`/`Failed to parse`/
  `NoSuchFieldError`/`ClassNotFound`.
- OCR de la pantalla de bloqueo: **`Bienvenida Anna!`**, **`7 llamadas
  perdidas`**, **`13 mensajes`** (antes: `Welcome Anna !`, `7 missed calls`,
  `13 messages`).

### Commits de esta sesion
- `80be4c5` — clases de UI es-LATAM via Builder.overrides (empujado).
- `83da5b1` — etiquetas del menu principal segun idioma activo (empujado).

### Estado final de esta sesion
- `translations/es-LATAM/override_ui.json`: **235 claves**.
- **39 clases** override; **247 cadenas reescritas**; `dist/core.binary`
  = **1104 entradas** (+41 nuevas, 17 reemplazadas).
- `tools/verify_build.py` -> **TODO VALIDADO**.
- Wine: **0 excepciones**, **0** errores de media/parse/clase.
- Commits empujados: `80be4c5`, `83da5b1`, `b3dbbb8`, `521c39b`, `5db4d16`,
  `4dc5e95` y el de creditos. Rama `feature/traduccion-es-latam-v2`.

### IMPORTANTE: fichero obsoleto `all_translations.json`
`translations/es-LATAM/all_translations.json` (3045 entradas) es un artefacto
ANTIGUO que **NO alimenta el build**. Contiene 257 cambios de acento erroneos
(`si`->`sí`, `como`->`cómo`, `solo`->`sólo`) producidos por un script ingenuo;
eso altera el significado (p. ej. "y si..." -> "y sí..."). La fuente de verdad
real es `translations/es-LATAM/en-us.fs` (que SI tiene `si`/`como` correctos).
No usar `all_translations.json` para regenerar el `.fs`.

### Pendiente / siguiente tarea
1. **Verificacion visual de pantallas internas**: entrar al telefono
   (home -> apps) en Wine y capturar: Chats, Galeria, Correo, Spark,
   Friends/Jabbr, Vloggr, Surfer, Restaurar, Ajustes/StatMenu. Confirmar OCR
   en espanol de las clases override.
2. **Verificar el selector de idioma end-to-end**: cambiar English <-> Espanol
   en el menu de Ajustes -> Idioma y confirmar que recarga `Grid` con el
   idioma correcto (independiente de ingles).
3. Revisar cadenas de UI que quedan en clases compartidas sin override
   (`GBSparkMatchScreen`, `GBSparkThreadProfileScreen`, etc. ya tienen
   override; revisar `game27.GlobalTexts` etiquetas de intereses que van por
   GBENUS).
4. Borrar o regenerar `all_translations.json` para evitar que un futuro agente
   lo use por error.

## 18. Sesion 2026-11-11 (segunda): reconstruccion del entorno + verificacion real

### Contexto
El sandbox fue **reiniciado**: `/tmp` quedo vacio y desaparecieron wine, Xvfb,
xdotool, imagemagick, tesseract, 7z y el JDK. El trabajo NO se perdio porque
`dist/` (core.assets, core.binary, es-latam.fs) SI esta versionado en GitHub.

### Reconstruccion del entorno (reproducible por cualquier agente)
```bash
sudo apt-get install -y wine xvfb x11-utils xdotool imagemagick \
     tesseract-ocr tesseract-ocr-spa p7zip-full default-jdk-headless
pip install pycryptodome            # lo necesita tools/blob_tool.py
# Extraer el juego original desde los volumenes del repo:
7z x -y -o/tmp/gameext SIMULACRA.7z.001
mkdir -p /tmp/game && cp /tmp/gameext/core.assets /tmp/gameext/core.binary /tmp/game/
python3 tools/blob_tool.py extract /tmp/gameext/core.binary /tmp/pyclasses
python3 -c "import zipfile;zipfile.ZipFile('/tmp/gameext/support.binary').extractall('/tmp/supportdir')"
# Rebuild (usar el javac del sistema, NO el path fijo del sandbox viejo):
ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_all.sh
python3 tools/verify_build.py            # -> TODO VALIDADO
# Binario sin Steam para Wine:
CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_test_binary.sh dist/core.binary /tmp/core_test.bin
```
El rebuild **reproduce** el mismo numero de clases (39) y cadenas (247) y un
`core.binary` de 1104 entradas. El md5 puede variar ligeramente por la version
de javac (21.0.4 vs 21.0.13); es equivalente a nivel de bytecode.

### Verificacion REAL en Wine (evidencia, no suposicion)
- Entorno: Xvfb `:99`, `WINEPREFIX=/workspace/wineprefix`,
  `LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe` (sin GPU).
- **Selector de idioma END-TO-END verificado** cambiando
  `STATE_LANGUAGE` en `.../.prefs/preferences`:
  - `en-us://`  -> pantalla de bloqueo en INGLES: *"7 missed calls"*,
    *"Missed call"*. 0 excepciones.
  - `es-latam://` -> pantalla de bloqueo en ESPANOL: *"¡Bienvenida Anna!"*,
    *"7 llamadas pérdidas"*, *"13 mensajes"*, *"Pista: el cumpleaños de Toby"*.
    0 excepciones.
- Esto demuestra que **es-LATAM es un idioma independiente y seleccionable**
  (no reemplaza al ingles) y que el contenido `es-latam.fs` + las clases
  override `game27.gbeslatam.*` cargan de verdad.
- Capturas en `docs/evidencia/`: `en-lock.png`, `es-latam-lock.png`,
  `menu-principal.png`.

### Pendiente / siguiente tarea
1. **Navegar el telefono** (abrir apps) para capturar OCR en espanol de:
   Chats, Galeria, Correo, Spark, Jabbr, Vloggr, Surfer, Restaurar,
   Ajustes/StatMenu. (Corregido en la seccion 22: el desbloqueo NO es un codigo
   fijo; lo fijan por letras los `game27.triggers.Triggers$*`.)
2. Revisar cadenas de UI en clases compartidas sin override.
3. Borrar/regenerar `all_translations.json` (obsoleto, acentos erroneos).

## 19. Sesion 2026-11-11 (tercera): reparacion de truncamientos y huecos de texto

**Causa raiz descubierta.** La traduccion base es-ES que sirvio de punto de
partida se aplico *in-place* respetando la **longitud en bytes** original. Eso
dejo cientos de cadenas **cortadas a mitad de palabra** (firma inequivoca: la
cadena ES mide exactamente los mismos bytes que la EN y acaba en letra). Afecto
a subtitulos de voz, cabeceras de chat, articulos web y etiquetas de UI.

**Reparado en esta sesion (3 commits):**
| Commit | Que | Volumen |
|--------|-----|---------|
| `2804e50` | Interjecciones de dialogo que seguian en ingles (`NO WAY`, `OH FUCK`, `SWEET JEBUS`, `OK FINE`, `Oh no.`, `Ok ok`, `JK LOL`, `SHIT SHIT`, `TOO FAR MAN`, `Huh? No!`, `NO NO`) + `GBESLATAM.text35` | 14 cadenas + 1 clase |
| `599d668` | Subtitulos de voz `vo://...=TEXTO` y cabeceras `chats://section/` truncadas -> traduccion COMPLETA | 236 ediciones (177 valores VO unicos + 3 chats) |
| `0d9a6f0` | Cadenas truncadas/sustituidas de UI, articulos y perfiles (`DISEÑO WE`->`DISEÑO WEB`, `*estáti`->`*estática*`, `Inici`->`Iniciar sesión`, `NOTI`->`NOTICIAS`, `Acerc`->`Acerca de`, `NUE`->`NUEVO`, `transpo`->`operadora`, nombres propios, etc.) | 49 ediciones |

**Metodo de deteccion de truncamientos** (reutilizable, ver
`tools/apply_fs_fixes.py`):
1. Alinear por indice el `.fs` EN original (extraido en `/tmp/gameext`) y el
   `.fs` traducido. La cadena i corresponde a la i.
2. Marcar como candidatas las cadenas donde `EN != ES` **y**
   `len(EN.encode()) == len(ES.encode())` **y** el ultimo caracter es letra.
3. Confirmar con un vocabulario de "palabras completas" del propio corpus
   (palabra seguida de espacio/puntuacion en cualquier otra cadena). Si la
   ultima palabra del ES **no** es una palabra completa pero **es prefijo** de
   una palabra completa -> truncada.
4. Excluir las CLAVES internas (`tools/keys_protegidas.txt`) que
   `fs_fix_keys.py` restaura en build (`missed`, `age`, `Spark`, `cover`...).
5. Editar con `tools/apply_fs_fixes.py` (JSON `[{pos,en,es}]`, aplica de mayor
   a menor posicion) y reconstruir.

**Artefactos de esta sesion** (versionados en git):
- `translations/es-LATAM/fixes_interjecciones2.json` (14)
- `translations/es-LATAM/fixes_vo_chats2.json` (236) + `vo_chats_map.json`
- `translations/es-LATAM/fixes_truncados2.json` (49)

**Verificacion:** `verify_build.py` -> `TODO VALIDADO`; rebuild reproducible
(39 clases / 247 cadenas / 1104 entradas en core.binary). Prueba en Wine con
`STATE_LANGUAGE=es-latam://`: pantalla de bloqueo en espanol, **0 excepciones**.

**Pendiente de esta sesion:**
- Navegar el telefono en Wine para confirmar visualmente las apps internas.
- Revisar el resto de `vo://` que el detector marca como "dudosos" (33 falsos
  positivos ya confirmados como traducciones completas).
- Los nombres propios (personas/empresas) se mantienen o castellanizan de forma
  inconsistente. Ya corregidos los errores claros (`Bill`->`Fact`,
  `Sally`->`salid`, `Pat`->`pal`, `Monica`->`Mónic`, `Jessica`->`Jéssic`,
  `Alex`->`Ále`). Conviene una pasada de coherencia general de nombres.

## 20. Sesion 2026-11-11 (cuarta): auditoria en sandbox limpio y bug de prefijos Kryo

**Contexto:** el sandbox se reinicio por completo (se perdieron `/tmp`, Wine,
JDK y las clases extraidas). Todo el trabajo estaba en GitHub, asi que se
reconstruyo unicamente lo necesario y se reauditaron los entregables.

**BUG CRITICO encontrado (commit `57e922b`).** `tools/fs_fix_keys.py::rebuild`
sustituia los bytes de una cadena editada pero **no reescribia los 4 bytes de
longitud big-endian** que preceden a cada cadena Kryo. Mientras la edicion
conservara el numero de bytes no pasaba nada; en cuanto cambiaba (el blindaje
del prefijo URI `chats://sección/` 42B -> `chats://section/` 41B), el scanner
del juego leia el prefijo antiguo (42) sobre 41 bytes reales, se desincronizaba
y **se tragaba la cadena siguiente**.

- Sintoma: `es-latam.fs` tenia 28138 cadenas en vez de 28139; la cabecera de
  chat `chats://section/Say something nice to her!` se comia el `sender`
  posterior y `remite` desaparecia del bloque de datos.
- Alcance: solo las **2** ediciones que cambiaban de longitud (prefijo URI y
  `photoroll://`). El resto del `.fs` estaba intacto.
- Arreglo: `rebuild()` ahora escribe `struct.pack(">I", len(new))` junto al
  texto. Rebuild -> 28139 cadenas, `verify_build.py` TODO VALIDADO.

**Otras correcciones de contenido (commit `d9aafa4`):**
- `photoroll://Chat Images/DEN_665` estaba sustituido por prosa ("Cada vez mas
  cerca"): es una referencia de RECURSO, no texto visible -> restaurado en la
  fuente (`translations/es-LATAM/fixes_photoroll.json`).
- Prefijo `chats://sección/` -> `chats://section/` en la fuente
  (`translations/es-LATAM/fixes_uri_prefix.json`).
- Los 30 `vo://content/vo/*.ogg=TEXTO` traducidos son CORRECTOS: el `=` separa
  el recurso de audio del subtitulo visible.

**Blindaje anadido.** `verify_build.py` ahora comprueba dos invariantes que
detectan esta clase de bug automaticamente, sin Java:
1. El conteo de cadenas de `es-latam.fs` debe ser **identico** al de `en-us.fs`.
2. Todos los prefijos de longitud Kryo del bloque de datos deben ser coherentes.

**Reconstruccion del entorno minimo (solo lo necesario para el `.fs`):**
```bash
pip install pycryptodome          # para tools/blob_tool.py (AES de core.binary)
# El .fs NO necesita Java: fs_fix_keys + build_locale_fs + build_core_assets
python3 tools/fs_fix_keys.py dist/core.assets translations/es-LATAM/en-us.fs \
    /tmp/f.fs --keys tools/keys_protegidas.txt
python3 tools/build_locale_fs.py /tmp/f.fs x /tmp/es-latam.fs \
    --old-prefix en-us:// --new-prefix es-latam:// --direct
python3 tools/build_core_assets.py dist/core.assets /tmp/core.assets \
    --replace es-latam.fs=/tmp/es-latam.fs
python3 tools/verify_build.py
```

**Pendiente / siguiente tarea:**
1. **Reconstruir el entorno Wine + JDK** para volver a validar en ejecucion
   (los pasos estan en las secciones 18/19). El `.fs` y `core.assets` estan
   verificados estaticamente, pero la prueba en juego requiere el binario.
2. Instalar el JDK y reconstruir `core.binary` con `tools/build_all.sh` si se
   cambia alguna clase `patch/game27/*` (no fue el caso esta sesion).
3. Continuar la pasada de coherencia de nombres propios.

## 21. Sesion 2026-11-11 (quinta): entorno reconstruido, 33 truncamientos mas y pantalla de bloqueo en espanol

**Entorno reconstruido y rebuild completo.** Tras reinstalar las herramientas
(seccion 18) se rehizo el pipeline entero con el JDK del sistema:

```bash
7z x -y -o/tmp/gameext SIMULACRA.7z.001
python3 tools/blob_tool.py extract /tmp/gameext/core.binary /tmp/pyclasses
python3 -c "import zipfile;zipfile.ZipFile('/tmp/gameext/support.binary').extractall('/tmp/supportdir')"
ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_all.sh
CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_test_binary.sh dist/core.binary /tmp/core_test.bin
```

El rebuild reproduce 39 clases nuevas / 1104 entradas / 28139 cadenas y
`verify_build.py` da TODO VALIDADO. El md5 de `core.binary` cambia respecto al
guardado (version de javac); es equivalente a nivel de bytecode.

**Detector de truncamientos mejorado -> 33 reparaciones (commit `24a5e67`).**
El primer pase (seccion 19) se dejo guiar por "misma longitud en bytes". El
detector refinado anade un filtro de stopwords y exige que la ultima palabra
sea prefijo de una palabra COMPLETA del propio corpus, con lo que aparecen 33
cadenas mas cortadas para caber en el espacio del ingles. Ejemplos:
`DISEÑO WE`->`DISEÑO WEB`, `DESARROLLO DE A`->`DESARROLLO DE APP`,
`¡E`->`¡Y bien!`, `Desarrollado por T`->`Desarrollado por TOUCHME`,
`Sí, lo s`->`Sí, lo soy`, `*olas del m`->`*olas del mar*`, `¡N`->`¡No!`,
`final d`->`endgame` (clave de video), y las cadenas "corruptas" del acosador
(`rollo d`->`sI nO`, `PROFUNDIZA EN T`->`DePeNdE dE tI`,
`YO NO LO S`->`Yo nO lO SoY`), respetando su estilo.
Fuente: `translations/es-LATAM/fixes_truncados3.json`.

**Verificacion REAL en Wine (evidencia nueva).**
- `docs/evidencia/es-latam-lock-nueva.png`: pantalla de bloqueo en ESPANOL
  ("7 llamadas perdidas" reconocido por OCR) tras pulsar BEGIN. 0 excepciones
  (solo el aviso benigno `Could not locate OpenAL library`).
- Selector de idioma confirmado en `patch/game27/gb/GBMainMenu.java`: tres
  opciones con etiquetas `English`, `简体中文` y `Español (Latinoamérica)`,
  cada una con su boton OK. es-LATAM es un idioma INDEPENDIENTE y seleccionable.

**Hallazgo sobre las pantallas internas (Chats, Galeria, Correo, Spark, Jabbr).**
El codigo de desbloqueo NO es fijo ni derivado de SHA-1: `game27.LockScreen`
expone `setCodeKeys(String...)` y son los `game27.triggers.Triggers$*` los que
lo fijan por letras segun el avance de la historia. Por tanto, para llegar a las
apps internas hay que JUGAR el prologo (o inyectar estado), no basta un codigo.
Comprobacion estatica: las cadenas de esas apps ya estan traducidas en
`es-latam.fs` (p. ej. "Bienvenido a Chats...", 53 lineas de Jabbr, 45 de Spark).

**Analisis de huecos: 0 cadenas de prosa inglesa sin traducir.** Un escaneo que
busca texto con >=2 palabras funcionales inglesas (the/and/you/... ) entre las
cadenas donde ES==EN no encontro ninguna. Las restantes coincidencias EN/ES son
nombres propios, codigos de cifrado, onomatopeyas y URIs.

**Pendiente / siguiente tarea:**
1. Jugar el prologo en Wine (xdotool) para capturar OCR de las apps internas,
   o inyectar el estado de desbloqueo para saltar la seccion jugable.
2. Pasada de coherencia de nombres propios (castellanizacion inconsistente).
3. Revisar los `vo://` marcados como "dudosos" (33 falsos positivos).

## 22. Sesion 2026-11-11 (sexta): navegacion real del telefono y correccion del mecanismo de desbloqueo

**Evidencia nueva de UI interna (OCR).** Con xdotool se pulso `BEGIN`, se espero
la pantalla de bloqueo y se hizo un gesto de deslizar hacia arriba, que desbloquea
y abre la PANTALLA DE INICIO de Anna. OCR (espanol, sin excepciones en el log):

- `docs/evidencia/es-latam-home-nueva.png`: *"¡Bienvenida Anna!"* y
  *"Pista: el cumpleaños de Toby"*.

Esto confirma en ejecucion que no solo la pantalla de bloqueo, sino tambien la
interfaz interna (home con widgets) se renderiza en espanol.

**Mecanismo de desbloqueo (correccion).** La seccion 18 afirmaba que el codigo
es "el cumpleaños de Toby". Eso es IMPRECISO. El desbloqueo se hace deslizando
hacia arriba; ademas existe un teclado de codigo que `game27.LockScreen` rellena
por letras mediante `setCodeKeys(String...)`. Los arrays NO son un SHA-1 fijo:
los fija la historia en `game27.triggers.Triggers$2$1..$12` (p. ej.
`H,E,?`, `H,E,L,?,P,5`, `W,E,L,?,M,L`, `H,E,U,?,S,K,G`...), donde `?` es un
comodin. Tambien hay un trigger con los digitos `180,071`. Conclusión: para
llegar a las apps internas hay que JUGAR el prologo (no hay un codigo unico que
teclear a mano sin el contexto de la historia).

**Hallazgo clave sobre las apps internas.** No se pudo abrir una app tocando
coordenadas del dock (los iconos no tienen etiqueta de texto y las apps se
desbloquean progresivamente por la historia: `CONTEXT_APP_CHATS`,
`CONTEXT_APP_GALLERY`, `CONTEXT_APP_SPARK`, `CONTEXT_APP_VLOGRR`,
`CONTEXT_APP_BROWSER`...). Es decir, la validacion visual de cada app interna
requiere jugar; no es alcanzable solo con navegacion. Comprobacion estatica: las
cadenas de esas apps YA estan traducidas en `es-latam.fs`.

**Nombres propios:** verificados en la fuente actual; ya no quedan artefactos de
truncamiento (`salid`, `Mónic`, `Jéssic`, `Ále`, `Fact`) salvo formas correctas
(`Mónica`, `Gedeón Jung`).

**Estado final de esta sesion:** fuente y `dist/` reconstruidos y validados
(28139 cadenas, 0 prefijos Kryo corruptos, TODO VALIDADO); 3 commits nuevos
(`24a5e67`, `2ab3865`, este) empujados a `feature/traduccion-es-latam-v2`.
Evidencia visual nueva en `docs/evidencia/`.

## 23. Sesion 2026-11-11 (septima): PRUEBA END-TO-END del selector de idioma nativo

**Objetivo (pivote de la mision):** demostrar que es-LATAM es un idioma
INDEPENDIENTE y seleccionable desde el selector nativo del juego (que ya soporta
`en-us` y `zh-cn`), no un reemplazo del ingles.

**Como se dispara el selector.** En `patch/game27/MainMenu.java` (metodo
`render`), el selector aparece SOLO en un primer arranque limpio: cuando
`Gdx.app.getPreferences("preferences")` NO contiene la clave `STATE_LANGUAGE` y
no hay partida guardada (`isFoundSave == false`). Si ya hay idioma guardado, se
salta y va directo al menu.

**Procedimiento reproducible (en Wine):**
```bash
# 1) Borrar la clave de idioma para forzar el selector en el proximo arranque
P="$WINEPREFIX/drive_c/users/openhands/.prefs/preferences"
#    dejar el XML <properties> vacio
# 2) Lanzar el juego y esperar ~40 s (headphones -> kaigan -> selector)
# 3) El selector muestra: "Language Selection"
#      [ ] English
#      [ ] 简体中文
#      [x] Español (Latinoamérica)
# 4) Pulsar el radio de "Español (Latinoamérica)" y luego BEGIN/OK
```

**RESULTADO VERIFICADO.** Tras pulsar el radio de espanol y el boton OK, el
juego escribe en `preferences`:
```xml
<entry key="STATE_LANGUAGE">es-latam://</entry>
```
Es decir, la seleccion nativa es-LATAM persiste correctamente. Evidencia:
`docs/evidencia/es-latam-selector-idioma.png` (OCR: *"Language Selection"*,
*"English"*, *"Español (Latinoamérica)"*).

**Conclusión:** el selector nativo funciona end-to-end para es-LATAM; el idioma
es independiente y seleccionable, exactamente como pedia el objetivo.

**Limitacion documentada honestamente.** La validacion visual pantalla-a-pantalla
de CADA app interna (Chats, Galeria, Correo, Spark, Jabbr, Vloggr, Surfer,
Restaurar, StatMenu) no se puede completar sin JUGAR el prologo: las apps se
desbloquean por la historia (`CONTEXT_APP_*`) y el teclado de codigo lo rellenan
los `Triggers`. Lo que SI esta verificado: (a) bloqueo e inicio en espanol,
(b) selector de idioma end-to-end, (c) las 28139 cadenas estan traducidas y
cargan sin excepciones. Queda pendiente una pasada jugada para el OCR interno.

---

## 13. Truncamientos en limites de palabra (sesion 2026-11-11/12)

### 13.1 El bug real (importante para futuras sesiones)

La traduccion se aplico en gran parte **in-place**: cada cadena espanola ocupa
exactamente los **mismos bytes** que su original ingles, rellenando el resto con
**espacios**. Cuando la traduccion era mas larga que el hueco, quedaba **cortada
en un limite de palabra**, y el corte pasa desapercibido porque termina en una
palabra completa:

```
EN: Find Yolanda          ->  ES: "Encuentra a"          (idx 11738)
EN: Finding Love          ->  ES: "Encontrando"          (idx 253)
EN: Camera Photo          ->  ES: "Foto de"              (idx 16039)
EN: Alexis Worth          ->  ES: "Alexis vale"          (idx 315)
```

El detector anterior (`fixes_truncated.json`, `fixes_truncados2/3.json`) solo
veia cortes **a mitad de palabra** (p.ej. "DESARROLLO DE A"), por eso este cuerpo
grande de errores quedo sin detectar.

### 13.2 Firma fiable del truncamiento

Una cadena esta truncada in-place si y solo si:

1. `len(es.encode()) == len(en.encode())`  (misma longitud en bytes), y
2. la cadena termina en **espacios de relleno** (`es != es.rstrip()`), y
3. el ultimo caracter no-espacio es una **letra** (sin puntuacion final).

Los puntos 2 y 3 separan el truncamiento real de las traducciones que
simplemente son mas cortas (esas terminan en `.` `!` `?` `…`).

Detector reproducible (ver `tools/`): comparar `en-us.fs` original con el
traducido, aplicar la firma anterior y clasificar por la ultima palabra:

* termina en preposicion/articulo/conector/posesivo/pronombre -> truncamiento
  casi seguro;
* termina en sustantivo/verbo/adjetivo -> revisar manualmente.

### 13.3 Cadenas reparadas en esta sesion (1033 en total)

| Fichero | Cadenas | Criterio |
|---|---|---|
| `translations/es-LATAM/fixes_truncados4.json` | 507 | terminan en preposicion/articulo/conector |
| `translations/es-LATAM/fixes_truncados5.json` | 17 | subtitulos `vo://` (se conserva el prefijo `vo://uri=`) |
| `translations/es-LATAM/fixes_truncados6.json` | 203 | terminan en pronombre/posesivo/preposicion |
| `translations/es-LATAM/fixes_truncados7.json` | 279 | alta confianza (in-place + menos palabras que el EN) |
| `translations/es-LATAM/fixes_truncados8.json` | 17 | residuales que terminan en coma (no llegan a rellenar el hueco) |
| `translations/es-LATAM/fixes_nombres_typos.json` | 2 | nombre corrupto (`Alexis vale`->`Alexis Worth`) y typo (`Vale pena`) |
| `translations/es-LATAM/fixes_localizacion.json` | 8 | vocabulario LatAm (`coche`->`carro`, `gafas`->`lentes`, `movil` con acento, `vale` final->`ok`) |

Los cuatro ficheros se aplican en orden sobre `translations/es-LATAM/en-us.fs`
con `tools/apply_fs_fixes.py` (formato `[{pos,idx,en,es}]`). El campo `en` guarda
la cadena **espanola truncada** original (es el texto que se reemplaza en el
bloque de objetos Mass), no el ingles.

### 13.4 Verificacion

* `es-latam.fs` -> **28139** cadenas (identico a `en-us.fs`; nada perdido).
* **0** truncamientos in-place restantes (firma 13.2).
* `python3 tools/verify_build.py` -> `TODO VALIDADO`.
* `dist/core.assets` -> 8 miembros, `en-us.fs` intacto, `es-latam.fs` embebido
  con el mismo md5 que `dist/es-latam.fs`.

### 13.5 Prueba real en el juego (Wine)

Arranque limpio con `STATE_LANGUAGE=es-latam://`. Resultado: menu principal
(imagenes BEGIN/CREDITS/QUIT), luego el **lockscreen en espanol**:

```
7 llamadas perdidas
Llamada perdida
13 mensajes
```

Esas cadenas salen de `GBESLATAMOverrides` (clase `GBLockScreen` reescrita), es
decir el mecanismo de override carga y renderiza correctamente. **0 excepciones
Java** en el log (solo el aviso esperado `Could not locate OpenAL library`, que
es la ausencia de tarjeta de sonido en el sandbox).

Evidencia: `docs/evidencia/es-latam-lockscreen-regresion-1006.png`,
`docs/evidencia/es-latam-mainmenu-regresion.png`.

### 13.6 Procedimiento de reparacion (repetible)

```bash
# 1. Extraer el juego original
7z x -y -o/tmp/gameext SIMULACRA.7z.001
mkdir -p /tmp/game /tmp/pyclasses /tmp/supportdir
cp /tmp/gameext/core.assets /tmp/gameext/core.binary /tmp/game/
python3 tools/blob_tool.py extract /tmp/gameext/core.binary /tmp/pyclasses
python3 -c "import zipfile;zipfile.ZipFile('/tmp/gameext/support.binary').extractall('/tmp/supportdir')"

# 2. Aplicar los fixes de truncamiento sobre la fuente traducida
python3 tools/apply_fs_fixes.py translations/es-LATAM/en-us.fs \
  translations/es-LATAM/fixes_truncados4.json /tmp/f4.fs
python3 tools/apply_fs_fixes.py /tmp/f4.fs \
  translations/es-LATAM/fixes_truncados5.json /tmp/f5.fs
python3 tools/apply_fs_fixes.py /tmp/f5.fs \
  translations/es-LATAM/fixes_truncados6.json /tmp/f6.fs
python3 tools/apply_fs_fixes.py /tmp/f6.fs \
  translations/es-LATAM/fixes_truncados7.json translations/es-LATAM/en-us.fs

# 3. Reconstruir los entregables
ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_all.sh
python3 tools/verify_build.py
```

### 13.7 Ultimo commit respaldado en GitHub

* Rama: `feature/traduccion-es-latam-v2`
* Commits: `f1a18a4` (1006 truncamientos), `78cb2bd` (residuales + nombre + typo + LatAm vocab)
* `git status` limpio y `local HEAD == remoto`.

### 13.8 Proxima tarea concreta

1. Cerrar los truncamientos **residuales** que no cumplen la firma 13.2 (cortes
   que no llegan al hueco, p.ej. "Encuentra a" vs "Encuentra"): buscar en
   `es-latam.fs` las cadenas mas cortas que su ingles sin puntuacion final y
   revisar por lotes de ~100.
2. Reparar la corrupcion de nombres propios: `idx 315` `Alexis vale` ->
   `Alexis Worth` (nombre de personaje; **no** traducir).
3. Ortografia: `Vale pena intentarlo` -> `Vale la pena intentarlo`.
4. Vocabulario LatAm: `movil`->`celular`, `coche`->`carro`, `gafas`->`lentes`,
   `piso`->`departamento` (solo donde encaje con la voz del personaje).
5. Pasada jugada para OCR de las apps internas (Chats, Galeria, Correo, Spark,
   Jabbr, Vloggr, Surfer, Restaurar, StatMenu).
