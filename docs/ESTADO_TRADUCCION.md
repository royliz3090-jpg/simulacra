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
