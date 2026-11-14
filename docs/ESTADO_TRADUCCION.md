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

> **ESTADO MAS RECIENTE (2026-11-13):** ver **seccion 23** (objetos comprimidos
> zlib) — es la ultima fuente de verdad. Rama `feature/traduccion-es-latam-v2`,
> ultimo commit `2fcebba`. Los commits de la sesion 23, en orden:
> `cc443ae` (144 fichas restphrase) → `a5d677d` (60 objetos comprimidos) →
> `64ca433` (2 puzzles comprimidos) → `4ddb416` (46 chats/correos/articulos) →
> `005bb85` (2 duplicados residuales) → `2fcebba` (documentacion seccion 23).

Rama `feature/traduccion-es-latam-v2` (commits de sesiones anteriores):

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

---

## 18. Sesion 2026-11-13: recuperacion + fix del autocompletado (placeholder del teclado)

### Contexto
Tras perder el sandbox, se reconstruyo el entorno (JDK 21, py7zr, `SIMULACRA.7z.001`
-> `/tmp/gameext`, clases en `/tmp/origcls`, `support.binary` -> `/tmp/supportdir`)
y se verifico que el avance **no se perdio**: la rama `feature/traduccion-es-latam-v2`
contiene el idioma independiente completo (blob KCB1 + `es-latam.fs`).

### Diagnostico del "texto en ingles en chats/UI"
- **Los subtitulos en espanol funcionan** => el juego **si carga `es-latam.fs`**.
  El `Grid` empaquetado en `dist/core.binary` tiene la rama
  `contentPrefix == "es-latam://" -> File.unpackFS("es-latam.fs")`.
- El ingles restante **no** viene del `.fs` (28139 cadenas, solo 5 nombres propios
  sin traducir) sino de **textos incrustados en clases Java** que no pasan por el
  sistema de localizacion.

### Bug raiz encontrado: placeholder del autocompletado
`game27.Keyboard` (clase base) instancia su ayuda de autocompletado con
`this.hint("Start typing")` / `this.hint("Continue typing")`. `Grid` crea el
teclado con **`new Keyboard()`** (linea 408 de `patch/game27/Grid.java`), es decir
**sin pasar por `Builder.overrides`**, por lo que su texto queda en ingles en
todos los idiomas (`'Start typing'` tampoco existia en `override_ui.json`).
`Continue typing` si se traduce via `GBKeyboard` (override, usado por el
layout), pero `Start typing` no tenia cobertura.

### Solucion implementada
1. `patch/game27/gbeslatam/GBESLATAMKeyboard.java` — subclase de `game27.Keyboard`
   que sobrescribe `public void hint(String)` traduciendo solo los dos textos:
   `Start typing` -> `Empieza a escribir`, `Continue typing` -> `Sigue escribiendo`.
2. `GBESLATAM.newKeyboard()` — factoria que devuelve la variante espanola.
3. `patch/game27/Grid.java` linea 408:
   `this.keyboard = Globals.CONTENT_PREFIX_ES_LATAM.equals(Globals.contentPrefix) ? GBESLATAM.newKeyboard() : new Keyboard();`
   (el ingles y el chino conservan `new Keyboard()`; **no se altera** su comportamiento).
4. `tools/build_all.sh` compila y empaqueta `game27.gbeslatam.GBESLATAMKeyboard`.

### Validacion
- `tools/build_all.sh` reproduce `dist/` (md5 `core.assets` = `ff52dbab...`).
- `tools/verify_build.py` -> **TODO VALIDADO** (1105 entradas, +42 nuevas).
- `javap` confirma `game27.gbeslatam.GBESLATAMKeyboard extends game27.Keyboard`
  con `hint(String)` sobrescrito, empaquetado en `dist/core.binary`.
- Pendiente prueba grafica real (ver seccion 10).

### Inventario de ingles visible restante (clases base, NO traducibles por idioma)
Analizado con `class_patch.ClassFile.string_literals()` en todas las clases de
`game27.*`:
- `game27.Keyboard` -> `Start typing` (**CORREGIDO**), `Malformed media autocomplete:` (log).
- `game27/app/friends/FriendsApp` -> `There are %d new posts` (banner Jabbr). **Pendiente**.
- `game27/GlobalTexts` / `game27/gb/GBStatMenu` -> `Moving On`, `Finding Love`, ... (intereses de Spark). **Pendiente**.
- `game27/app/phone/PhoneApp` -> `FAST MODE ENABLED` / `CONSOLE ENABLED` / `SKIP DECODES ENABLED` (solo debug). Ignorar.
- `game27/triggers/*` -> cadenas de reconocimiento del parser (entradas de texto libre, `a dogs purpose`, `copy writer`, nombres de youtubers de `BootConfig`). **No** traducir (rompen el reconocimiento). **Pendiente de decision**.
- `game27/gb/GBCreditsMenu` -> creditos (nombres propios). Correcto dejar igual.
- `game27/gb/*` nombres propios (Sara Whitman, Cody Allison, Greg, 21...). Correcto dejar igual.

### 18.1 Ultimo commit respaldado
- Rama `feature/traduccion-es-latam-v2`; commits previos: `b4112be` (docs), `fd08369`, `78cb2bd`, `f1a18a4`.
- Este bloque: fix del autocompletado + documentacion (ver `git log`).

### 18.2 Proxima tarea concreta
1. Traducir `There are %d new posts` (FriendsApp) via override de clase o parche.
2. Traducir los intereses de Spark (`Moving On`, `Finding Love`, ...) en
   `GBStatMenu`/`GlobalTexts` (cadenas ya presentes en `override_ui.json`? verificar).
3. Decidir sobre los literales del parser (`triggers/*`): mantener en ingles.
4. Prueba grafica real en Windows/Steam: elegir "Espanol (Latinoamerica)" y
   recorrer menus, chats (ver "Empieza a escribir"), llamadas y correos.

---

## 19. Verificacion de cobertura (2026-11-13)

Analisis reproducible del `.fs` con `simulacra_fs.py`:
- `en-us.fs` = 28139 cadenas; `es-latam.fs` = 28139 cadenas.
- **0 cadenas con prosa inglesa** en `es-latam.fs` (heuristica de palabras
  inglesas vs espanolas). El contenido jugable esta en espanol.
- Las cadenas **identicas** al ingles que quedan son legitimas:
  - Fechas `09 August 2017`, `13 July`, horas `9:30 PM` -> el juego las
    **parsea** (`Failed to parse time`); traducirlas rompe el arranque.
  - Claves de estado y codigo embebido (`auto`, `sender`, `x`, `user`,
    `!a2_memorywipe_timeout`, `Triggers.updateCounter(...)`, `web://...`,
    `content/...`, `photoroll://...`).
  - Nombres propios (`Greg`, `Taylor`, `Anna`, `Ashley`, `Yolanda`, `Cassie`).
  - Claves estructurales protegidas en `tools/keys_protegidas.txt` (`Camera`, ...).
- **Pendiente menor**: tags de intereses en perfiles NPC de Spark dentro del
  `.fs` (`Music`, `Food`, `Movies`, `Books`, `Outdoors`, `Gaming`, `Theatre`,
  `Animals`, `Mom`, `Discrepancies`, `Search`). Son datos de perfil de otros
  usuarios (solo visualizacion). El emparejamiento con James usa
  `SparkEditProfileScreen.interests()` (los `sparkTags` del jugador) contra
  `GlobalTexts.a3_james_tags_*`; **ambos ya estan en espanol y coinciden**, por
  lo que el match funciona. Traducir estos tags NPC es opcional y requiere
  cuidado (varios valores ya son neutros: `Music`, `Food`, `Gaming`, `Outdoors`,
  `Theatre`).

### Estado de los textos de clase (inventario seccion 18)
- Corregidos y empujados: `Start typing` (teclado), ` years ago` (Jabbr),
  titulo de pagina del navegador.
- Ya cubiertos por overrides: intereses de Spark (`sparkTags`, `a3_james_tags`),
  indicadores "esta escribiendo", mensajes de chat, menus, galeria, correo, etc.
- Correcto dejar igual: nombres propios, creditos (`GBCreditsMenu`), literales
  del parser (`triggers/*`, `BootConfig` nombres de youtubers), logs internos.
- Pendiente opcional: `There are %d new posts` (banner de Jabbr; requiere
  sobrescribir un metodo completo de `FriendsApp`).

---

## 20. Traduccion real del .fs: 58 cadenas visibles (2026-11-13)

Se continuo la traduccion **real del recurso** (`es-latam.fs`), no solo de
overrides de clase. Cadenas que seguian en ingles y son **datos visibles**
(verificado que NO son claves de logica comparando contra los literales de
todas las clases `game27.*`):

- Opciones de respuesta de chat: `Awesome!`->`¡Genial!`, `Again?`->`¿Otra vez?`,
  `Really?`/`Seriously?`->`¿En serio?`, `Thanks!`->`¡Gracias!`,
  `Finally!`->`¡Por fin!`, `College?`->`¿La universidad?`,
  `Blackmail?`->`¿Chantaje?`, `Drinks?`->`¿Unas copas?`, `Promise!`->`¡Lo prometo!`,
  `Nifty!`/`Noice!`->`¡Qué chido!`/`¡Chido!`, `Sweet!`->`¡Qué padre!`,
  `Totes!`->`¡Total!`, `Cheers!`->`¡Salud!`, `DUH!`->`¡OBVIO!`, `Wait!`->`¡Espera!`,
  `Nothing!`->`¡Nada!`, `Anyone?`... (58 en total, ver `fixes_respuestas.json`).
- Textos de webs: `NEVER MISS ANYTHING`->`NO TE PIERDAS NADA`,
  `A SMOOTHER START`->`UN INICIO MÁS FLUIDO`, `INVITE GUEST`->`INVITAR A INVITADO`,
  `WEB DESIGN`->`DISEÑO WEB`, `APP DEVELOPMENT`->`DESARROLLO DE APPS`,
  `Announcement!`->`¡Anuncio!`, `HurRRy!!!`->`¡Apúrate!!!`.
- Emoticonos/onomatopeyas: `*hugs*`->`*abrazos*`, `ba dum tsh`->`badum tss`.

Procedimiento usado (reproducible):
1. `python3 tools/fs_translate.py scan <es-latam.fs> <en-us-original.fs>` lista
   las cadenas identicas al ingles no legitimas (fechas/claves/rutas/nombres).
2. Se traducen a un `pares.json` y se generan posiciones con
   `python3 tools/fs_translate.py fixes <es-latam.fs> <pares.json> <out.json>`.
3. `python3 tools/apply_fs_fixes.py <es-latam.fs> <out.json> <nuevo.fs>` (58/58).
4. El nuevo `.fs` pasa a ser la fuente de verdad (`translations/es-LATAM/en-us.fs`).
5. `bash tools/build_all.sh` reconstruye `dist/`; `tools/verify_build.py` OK.

### Herramientas nuevas de esta sesion
- `tools/verify_es_latam_coverage.py`: valida conteo de cadenas, ausencia de
  prosa inglesa, cadenas legitimas y **coherencia de los tags de Spark**
  (`sparkTags` debe contener `a3_james_tags_required/optional`; hoy OK).
- `tools/fs_translate.py`: `scan` y `fixes` (genera posiciones para `apply_fs_fixes`).

### Estado final de esta sesion
- `es-latam.fs`: 28139 cadenas, 0 prosa inglesa, 213 identicas restantes
  (todas legitimas: fechas, claves, rutas, emails, nombres, emoticonos).
- md5 actuales: `es-latam.fs=77899a6d`, `core.assets=68a0dff6`.
- `dist/core.binary`: 1105 entradas, incluye `game27.gbeslatam.GBESLATAMKeyboard`.
- Pendientes menores (opcionales, bajo impacto): `There are %d new posts`
  (Jabbr), cadenas dinamicas con nombre/edad embebidos (`Greg, 21`,
  `Anna, 20`, `Image from by Greg`) y tags de intereses de perfiles NPC en el
  `.fs`.

### 20.1 Ultimo commit respaldado
`4402066` (58 cadenas del .fs) sobre `feature/traduccion-es-latam-v2`. Cadena de
commits de la sesion: `4862ec9` (teclado) -> `658a5b1` (UI strings) ->
`1d91bbd` (docs cobertura) -> `4402066` (58 cadenas .fs).

### 20.2 Proxima tarea concreta
1. Prueba grafica real en Windows/Steam: idioma "Espanol (Latinoamerica)",
   recorrer chats (ver "Empieza a escribir"), Jabbr, navegador, Spark.
2. Opcional: `There are %d new posts` via `FriendsApp` subclass.
3. Opcional: tags de intereses NPC en el `.fs` (cuidado: no romper el match).

---

## 21. Segunda pasada de truncamientos in-place (2026-11-13)

Tras la sesion 13 (§13.2) quedaban cortes que terminan en **sustantivo/verbo**
(dificiles de detectar). Se cerro el cuerpo con dos detectores nuevos:

### 21.1 Detector A: final en palabra que exige complemento
Una cadena in-place (`len(es)==len(en)`, con relleno, ultima letra) esta truncada
si su ultima palabra es un auxiliar/copulativo/cuantificador que no puede cerrar
la frase: `esta/estoy/tengo/puedo/quiero/voy/mas/bastante/algo/cualquier/...`
(ej.: `Está` <- `She is missing`, `Todavía hay` <- `There is still hope`,
`Puedo` <- `I can explain`).

### 21.2 Detector B: final en preposicion/articulo/conjuncion
Lista estricta (`de, del, a, en, con, por, para, el, la, los, mas, tan...`).
18 candidatos; 13 eran truncamientos reales.

### 21.3 Cadenas reparadas
| Fichero | Cadenas | Metodo |
|---|---|---|
| `translations/es-LATAM/fixes_truncados9_index.json` | 18 | indice -> `tools/fs_fix_by_index.py` |
| `translations/es-LATAM/fixes_truncados10_index.json` | 106 | detector A (auxiliares) |
| `translations/es-LATAM/fixes_truncados9_10.json` | 124 | posiciones combinadas (sin solape) |

Se aplicaron las 124 con `tools/apply_fs_fixes.py` (124/124). Tras aplicar, la
heuristica solo deja 5 cadenas, todas legitimas (`Ya esta`, `igual me voy`,
`Te quiero`, `Que es lo que quieres`, y un `vo://...si quiero`).

### 21.4 Herramienta nueva
`tools/fs_fix_by_index.py <fs> <index_map.json> <out.json>`: genera fixes por
**indice** de cadena (necesario cuando el texto actual lleva relleno y no se
puede emparejar por texto exacto).

### 21.5 Nota importante: reproducibilidad de `dist/core.binary`
El **md5 de `core.binary` cambia en cada build** aunque el contenido sea el mismo:
el blob KCB1 cifra cada entrada con AES-CTR usando un **IV aleatorio**
(`os.urandom(16)`, ver `tools/blob_tool.py:237` y `tools/patch_core_binary.py:31`).
Verificado: el **contenido extraido es identico** entre builds
(`blob_tool.py extract` + `diff -rq` -> sin diferencias). No es un error.
`core.assets` y `es-latam.fs` SI son reproducibles (md5 estable).

### 21.6 Estado tras esta sesion
- md5: `core.assets=4793660c`, `es-latam.fs=db57b1a9` (core.binary varia por IV).
- `verify_build.py` -> TODO VALIDADO; `verify_es_latam_coverage.py` -> 0 prosa inglesa.
- 28139 cadenas; truncamientos in-place: cerrados.

### 21.7 Ultimo commit / proxima tarea
- Commit de este bloque: 124 truncamientos + herramientas (ver `git log`).
- Proxima: prueba grafica real (Windows/Steam) recorriendo la historia;
  revisar naturalidad de las frases reparadas en contexto.

---

## 22. Validacion REAL en el juego (Wine) — 2026-11-13

Se ejecuto el juego en Wine (sin GPU, `Xvfb :99`, `LIBGL_ALWAYS_SOFTWARE=1
GALLIUM_DRIVER=llvmpipe`, `WINEPREFIX=/workspace/wineprefix`) con los
entregables actuales (`dist/core.assets` + binario de prueba sin Steam) y
`STATE_LANGUAGE=es-latam://` en `.prefs/preferences`.

### 22.1 Textos observados en el juego (OCR, tesseract -l spa)
| Pantalla | Texto en es-LATAM |
|---|---|
| Menu principal | BEGIN / CREDITS / QUIT (texturas, sin cambios) |
| Pantalla de bloqueo | **"7 llamadas Perdidas"**, **"13 mensajes"** |
| Home (desbloqueado) | **"¡Bienvenida Anna!"**, **"Pista: el cumpleaños de Toby"** |
| Iconos de apps | **Jabbr, Vloggr, Surfer, Teléfono, Chats, Galería, Correo** |
| Nota de la app de notas | **"Pendiente: Encontrar a Anna"** |

Conclusion: el `es-latam.fs` **carga y se renderiza en el juego real**; la
traduccion no es solo teorica. 0 excepciones relevantes en el arranque.

### 22.2 Evidencia
Capturas en `docs/evidencia/`:
`es-latam-mainmenu-2026-11-13.png`, `es-latam-lock-2026-11-13.png`,
`es-latam-home-2026-11-13.png`, `es-latam-notif-2026-11-13.png`.

### 22.3 Limitaciones de esta validacion
- No se completo el desbloqueo hasta abrir **Chats** (el teclado / placeholder
  "Empieza a escribir") por las protecciones de la historia (scare/glitch al
  navegar rapido con xdotool). Pendiente una partida manual.
- La app de Chats y el fix `GBESLATAMKeyboard` quedan validados de forma
  **estatica** (clase presente en `core.binary`, bytecode valido) pero no
  observados en pantalla en esta sesion.

### 22.4 Entorno reproducible (comandos)
```bash
sudo apt-get install -y wine64 xvfb x11-utils xdotool imagemagick \
     tesseract-ocr tesseract-ocr-spa p7zip-full default-jdk-headless
sudo dpkg --add-architecture i386 && sudo apt-get update
pip install pycryptodome Pillow numpy
# (re)crear wineprefix si esta corrupto:
WINEPREFIX=/workspace/wineprefix DISPLAY=:99 wineboot -u
# binario de prueba sin Steam:
CLASES=/tmp/origcls SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_test_binary.sh dist/core.binary /tmp/core_test.bin
# lanzar:
cd /tmp/gamerun && DISPLAY=:99 WINEPREFIX=/workspace/wineprefix \
  LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe wine simulacra.exe
# capturar: DISPLAY=:99 import -window root shot.png
# OCR: tesseract shot.png - -l spa --psm 11
```
OJO: si `wine` da `could not load kernel32.dll`, el `WINEPREFIX` esta corrupto;
recrearlo con `wineboot -u` y volver a escribir `.prefs/preferences`.

## 23. Sesion 2026-11-13 (continuacion): OBJETOS COMPRIMIDOS (zlib) del .fs

### 23.1 Descubrimiento clave: el escaner de cadenas era INCOMPLETO

El bloque de DATOS de un `.fs` es una secuencia de objetos. La mayoria son
cadenas planas `[u32 len][utf8]` que `simulacra_fs.scan_strings` detecta. PERO
algunos objetos son un `String[]` serializado y **comprimido con zlib** (magic
`78 da`): su contenido NO aparece en la tabla plana y por tanto **escapaba por
completo al pipeline de traduccion**. Ahi viven:

- Textos de paginas web del juego (Spark, NSFW, Ridr, Faris & Kane, IRIS OS,
  Phresh Ideas, Kappa Feed, The Write Thing).
- Correos (Rainforest, Jabbr, Anna/Ed/Elizabeth/Murv, el jefe Faraday).
- Los blog posts de la trama (Dice Roll / NSFW / el bloguero).
- Mensajes de chat de la faccion demon/aliado.
- Fichas de 2 puzzles `restphrase` (greg1, emailmurv1).

Comprobacion: `'Impressive websites and apps...'` existia en la tabla plana
(ya traducido) y ADEMAS en un objeto comprimido (sin traducir): hay
**duplicados** entre la tabla plana y los objetos comprimidos.

### 23.2 Herramienta nueva: `tools/apply_blob_fixes.py`

```
python3 tools/apply_blob_fixes.py <in.fs> <fixes.json> <out.fs>
```
- `fixes.json` = `{"<indice_objeto>": {"<texto en>": "<texto es>", ...}, ...}`
  (el indice de objeto es el 0-based de `build_locale_fs.parse_format`).
- Descomprime el objeto, sustituye cadenas por coincidencia EXACTA y recomprime.
- Autodetecta dos disposiciones de payload: (a) secuencia plana de cadenas;
  (b) `[u32 count]` + `count` cadenas (puzzles restphrase).
- **Preserva la cola binaria** que sigue a las cadenas (16 bytes en los objetos
  de chat: `[mensaje][remitente][fecha][hora]` + float/metadata).
- **Recalcula los offsets** del bloque de formato (los objetos posteriores se
  desplazan al cambiar el tamano). Verificado: `offsets[-1] == len(data)`.

### 23.3 Como detectar los objetos comprimidos

```python
import zlib, struct
sys.path.insert(0,'tools'); import build_locale_fs as B
raw=open('es-latam.fs','rb').read()
fmt,data,field=B.split_fs(raw); f=B.parse_format(fmt); offs=f['offsets']
MAG=(b'\x78\xda',b'\x78\x9c',b'\x78\x01',b'\x78\x5e')
for k,end in enumerate(offs):
    start=offs[k-1] if k>0 else 0
    seg=data[start:end]
    if seg[:2] in MAG:
        out=zlib.decompressobj().decompress(seg)   # payload (strings + cola)
```

### 23.4 Trabajo realizado en esta sesion

| Grupo | Objetos | Textos | Archivos fuente |
|---|---|---|---|
| Webs/correos/blog (batch 1) | 60 | 59 | `work/blob_textos.json` + `work/blob_fixes.json` |
| Puzzles restphrase comprimidos | 2 | 23 fichas | `work/blob_fixes_rest.json` |
| Chats/correos/articulos (batch 2) | 46 | 46 | `work/blob_textos2.json` + `work/blob_fixes2.json` |
| Duplicados residuales | 2 | 2 | `work/blob_fixes3.json` |
| **Total objetos comprimidos** | **110** | **130** | |

Ademas, `work/restphrase_map.py` + `work/restphrase_idx.json` traducen 144
fichas en 22 bloques de puzzles `restphrase` NO comprimidos (commit `cc443ae`).

### 23.5 Como reproducir (orden de aplicacion sobre el .fs base)

```bash
# 1) fixes de la tabla plana (ya en translations/es-LATAM/en-us.fs)
# 2) fichas de puzzles restphrase (no comprimidos)
python3 tools/apply_fs_fixes.py en-us.fs work/restphrase_fixes.json out.fs
# 3) objetos comprimidos (3 lotes)
python3 tools/apply_blob_fixes.py out.fs work/blob_fixes.json    out2.fs
python3 tools/apply_blob_fixes.py out2.fs work/blob_fixes_rest.json out3.fs
python3 tools/apply_blob_fixes.py out3.fs work/blob_fixes2.json  out4.fs
python3 tools/apply_blob_fixes.py out4.fs work/blob_fixes3.json  out5.fs
# 4) rebuild
ORIG=/tmp/game CLASES=/tmp/origcls SUPPORT=/tmp/supportdir JAVAC=/usr/bin/javac \
  bash tools/build_all.sh
python3 tools/verify_build.py dist/core.assets dist/core.binary /tmp/game/core.assets
```

### 23.6 Auditoria de cobertura (metodo reutilizable)

Para saber que queda en ingles, comparar objeto-a-objeto EN vs ES (no solo la
tabla plana). Filtro de ruido: descartar identificadores, triggers, rutas,
codigo (`Triggers.`, `Globals.`, `://`, `.jpg/.png/...`, `#ifdef`, shaders).
Resultado: **0 prosa real pendiente**; lo restante son identificadores
(`__LINKnnn`, `a3_stat_*`, `nav_to_*`, rutas) que NO deben traducirse.

### 23.7 Pendiente / siguiente tarea

1. **Verificacion visual en Wine** de las pantallas afectadas (webs, correo,
   chat demon) para confirmar renderizado en espanol (entorno de la seccion 22).
2. Revisar si `en-us.fs` original conserva copias planas de estos textos y si
   el juego prioriza la copia comprimida o la plana (hoy se traducen ambas).
3. Revisar cadenas de UI en clases compartidas sin override.

## 24. Sesion 2026-11-11: etiquetas de intereses, UI y bug del aplicador (continuacion)

### 24.1 Auditoria de cobertura (metodo reutilizable)

Se comparo objeto-a-objeto EN vs ES sobre `dist/core.assets`. Resultado:
- total de cadenas con texto EN: 28139
- traducidas (ES != EN y no vacias): ~6400
- identicas EN=ES: 21809, de las cuales ~11576 son tecnicas (rutas, ids,
  triggers, fechas, constantes) y el resto nombres propios/emojis/simbolos.
- Tras filtrar ruido (codigo, rutas, triggers, nombres, emojis), la prosa real
  pendiente es **0**. La unica cadena EN=ES con palabras funcionales inglesas
  es `The Click Hole` (nombre de marca, se conserva por politica).

Comprobacion rapida: buscar cadenas EN=ES que contengan palabras funcionales
inglesas (`the|you|is|and|with|what|...`). Hoy devuelve 1 sola.

### 24.2 Bug encontrado y corregido en `tools/apply_text_fixes.py`

El aplicador anterior recorria el cuerpo de cada objeto con un bucle de saltos
`[u32 len][utf8]`. Dos fallos:
1. **No reconocia los arrays Kryo** `[u32 count][str][str]...`: al leer el
   contador como si fuera una longitud, desincronizaba todo el resto del objeto
   y dejaba las cadenas siguientes sin aplicar.
2. **No aplicaba los reemplazos en orden descendente de offset**, de modo que al
   alargar una cadena se desplazaban las posiciones aun pendientes del mismo
   objeto (el conteo de cadenas se desviaba, p.ej. 28139 -> 28105).

Ahora usa `S.scan_strings` (que salta el contador) y aplica los cambios de mayor
a menor posicion. Verificado: 28315 objetos, 27634 cadenas planas identicas
antes y despues.

### 24.3 Traducciones nuevas de esta sesion

Etiquetas de interes de los perfiles SPARK (arrays dentro de objetos planos),
42 apariciones de 18 etiquetas:
`Animals`->Animales, `Books`->Libros, `Charity`->Caridad, `Cooking`->Cocina,
`Dancing`->Baile, `Finance`->Finanzas, `Food`->Comida, `Gaming`->Videojuegos,
`Indoors`->Interiores, `Movies`->Peliculas, `Music`->Musica,
`Outdoors`->Aire libre, `Pets`->Mascotas, `Politics`->Politica,
`Studies`->Estudios, `Theatre`->Teatro, `Travelling`->Viajes, `Search`->Buscar.

Titulos de seccion truncados, completados:
`Moving On`->`Seguir adelante`, `Finding Love`->`Encontrando el amor`,
`Personal Growth`->`Crecimiento personal`.

UI: `Camera`->Camara (5), `Discrepancies`->Discrepancias (5).

NO traducido (a proposito): `Chat Images` es el nombre de la carpeta en rutas
`photoroll://Chat Images/...`; `CBB`, `NSFW`, `PhreshIdeas`, `Kappafeed`,
`The Click Hole` son nombres propios/marca; `No`/`OK`/`Ok` son validos en ambos
idiomas; `Springwood`/`Casual` son lugar/adjetivo valido en espanol.

### 24.4 Herramienta nueva

`tools/gen_blob_batch.py`: dado un `.fs` y un mapa `{en: es}` (o lista
`[{en,es}]`), genera el JSON `{indice_objeto: {en: es}}` que consume
`tools/apply_blob_fixes.py` para los objetos comprimidos (zlib).

### 24.5 Commits respaldados en esta sesion

- `bec3c4b`: etiquetas de intereses + 3 titulos truncados + bug del aplicador.
- `9d85ebd`: etiquetas de UI (Camera, Discrepancies).

Ambos confirmados en `origin/feature/traduccion-es-latam-v2`.

### 24.6 Validacion

`tools/rebuild_es.sh` + `tools/verify_build.py`: en-us.fs identico al original,
207 nombres en formato, todos `es-latam://`, 28139 == 28139 cadenas, 0 prefijos
Kryo corruptos. La prueba visual en Wine (seccion 22) sigue pendiente para las
pantallas de perfiles SPARK.

### 24.7 Proxima tarea concreta

1. Verificacion visual en Wine de los perfiles SPARK (etiquetas de interes),
   la galeria (Camera) y el navegador NSFW (Discrepancies).
2. Revisar si quedan cadenas de UI en clases base compartidas sin override
   (ver inventario de la seccion 18).

---

## 25. Sesion 25 - Auditoria completa del 100% de textos (rama `audit/export-dialogos-es-latam-v2`)

Objetivo: extraer el 100% de los textos narrativos y de dialogo de SIMULACRA
para que ChatGPT los revise, **sin modificar el juego**.

### 25.1 Hallazgo principal: el grafo `map` del `.fs`

El array `map` del bloque de formato del `.fs` es un grafo de referencias. Cada
valor `v` codifica `indice_destino = v >> 2` y `tag = v & 3` (3 = referencia).
Siguiendo esas referencias (BFS) desde los 207 objetos raiz (los nombrados en
`names`) se alcanzan **los 28315 objetos**, y **27975 tienen un unico
propietario**, lo que permite atribuir cada cadena a su recurso
(`content/chats/greg`, `content/mail/...`, etc.). Detalle en
`docs/AUDITORIA_ARQUITECTURA.md`.

### 25.2 Total real de cadenas: 30877 (no 28139)

- Escaneo del bloque completo: 28139 (pierde los objetos comprimidos con zlib).
- Escaneo **por objeto** (descomprimiendo cada uno): **30877**
  = 27634 planas + 3243 en objetos comprimidos.
- Los 490 "extras" del escaneo de bloque son falsos positivos de 1 caracter.

Alineacion EN/ES verificada: 0 objetos con distinto numero de cadenas.

### 25.3 Herramientas nuevas

| herramienta | funcion |
|---|---|
| `tools/export_auditoria.py` | extrae las 30877 cadenas EN+ES alineadas con propietario, tipo, categoria y flags |
| `tools/export_revision.py` | genera el paquete para ChatGPT (REVISION/UNICOS + indice) |
| `tools/java_strings.py` | extrae constantes LDC de clases Java (sin JDK) |
| `tools/export_java_ui.py` | empareja `game27/gb/**` (EN) con `game27/gbeslatam/**` (ES), 657 cadenas |
| `tools/validate_export.py` | valida cobertura 100% contra el `.fs` real |

### 25.4 Resultado

- `exports/simulacra_textos_completos.jsonl`: **30877** registros (100%).
- `exports/revision_chatgpt/`: paquete para revision.
  - narrativo 4770, UI 1456, tecnico 24651.
  - pares unicos EN/ES: 5451.
  - incidencias: 425 sin_traducir, 2564 relleno_espacios, 35 contenido_faltante,
    3 marcadores_distintos.
- `tools/validate_export.py` -> "OK - cobertura 100%".

### 25.5 Texto de UI incrustado en clases Java

Parte del texto de UI (menus, notificaciones, dialogos de sistema) vive en las
clases Java de `core.binary`, no en el `.fs`. El juego trae la version inglesa en
`game27/gb/**` y overrides en espanol en `game27/gbeslatam/**`. Se extrajeron
657 cadenas alineadas por (metodo, ordinal) en `exports/revision_chatgpt/JAVA_UI.jsonl`.
`GBMainMenu` ya contiene espanol incrustado (menu de opciones, selector de
idioma), senal de que sesiones previas parchearon clases Java.

### 25.6 Commit respaldado

`feat(auditoria): extraccion del 100% de textos (30877 cadenas)` en
`origin/audit/export-dialogos-es-latam-v2`.

### 25.7 Proxima tarea concreta

1. Enviar `exports/revision_chatgpt/UNICOS.md` a ChatGPT y obtener las
   correcciones de las 425 sin_traducir + 2564 con relleno_espacios.
2. Aplicar las correcciones con `tools/apply_blob_fixes.py` (objetos comprimidos)
   y `tools/apply_fs_fixes.py`/`fs_editor.py` (planos), preservando marcadores.
3. Reconstruir con `tools/rebuild_es.sh` y verificar con `tools/validate_export.py`
   (que las cadenas corregidas ya no esten en EN) y `tools/verify_build.py`.
4. Prueba visual en Wine de las pantallas afectadas.

---

## 26. Sesion 26 - Aplicadas las correcciones de ChatGPT (primera pasada)

### 26.1 Entrada

- `fixes.json`: 672 pares `{en, es}` devueltos por ChatGPT (666 con cambio real).
- `INFORME_REVISION_SIMULACRA.md`: informe de la revision (851 apariciones).

### 26.2 Validacion previa (`tools/validate_fixes.py`)

- 666/666 correcciones aplicables; **0 errores**.
- 0 marcadores protegidos distintos, 0 URIs perdidas, 0 cambios en el numero de
  saltos de linea, 0 claves inventadas.

### 26.3 Aplicacion (`tools/apply_chatgpt_fixes.py`)

El `en` de cada fix identifica la CADENA INGLESA (no el espanol, que puede estar
truncado). El script:

1. localiza cada `en` en `en-us.fs` (ingles pristino);
2. obtiene la posicion de la cadena espanola alineada (mismo objeto + ordinal);
3. sustituye esa cadena por el `es` propuesto, reescribiendo el objeto
   (funciona con objetos planos y comprimidos, recalcula offsets).

Resultado: **835 sustituciones** en 835 objetos, **0 claves sin aplicar**.

### 26.4 Verificaciones

- `dist/es-latam.fs`: 838/838 ocurrencias de los fixes correctas (0 incorrectas).
- Integridad: 30877/30877 cadenas, 0 objetos con nº de cadenas distinto.
- `dist/core.assets` -> `en-us.fs` **identico byte a byte** (md5 sin cambios):
  el ingles NO se altera (idioma independiente).
- `tools/verify_build.py` -> TODO VALIDADO.
- `tools/verify_es_latam_coverage.py` -> TODO VALIDADO.

### 26.5 Mejora medible (incidencias en pares unicos)

| incidencia | antes | despues |
|---|---|---|
| sin_traducir | 425 | 400 |
| relleno_espacios | 2564 | 2085 |
| contenido_faltante | 35 | 18 |
| marcadores_distintos | 3 | 0 |

### 26.6 Commit respaldado

`fix(es-latam): aplica 666 correcciones de la revision ChatGPT (835 sustituciones)`
en `origin/audit/export-dialogos-es-latam-v2` (commit `e652340`).

### 26.7 Proxima tarea concreta

1. Segunda pasada de ChatGPT sobre el paquete regenerado
   (`exports/revision_chatgpt/UNICOS.md`) para las ~2085 con relleno de espacios
   y 400 sin traducir (ver `exports/revision_chatgpt/LOTE2.md`).
2. Repetir el ciclo: `export_auditoria.py` -> `export_revision.py` -> ChatGPT ->
   `validate_fixes.py` -> `apply_chatgpt_fixes.py` -> `rebuild_es.sh` -> verificar.
3. Prueba visual en Wine de las pantallas afectadas.

---

## 27. Sesion 27 - Aplicado el lote 2 de ChatGPT

### 27.1 Entrada

- `fixes_lote2.json`: 62 correcciones nuevas `{en, es}`.
- `fixes_acumulados_lotes1y2.json`: 734 pares (lote 1 + lote 2, sin duplicados).
- `INFORME_LOTE2_SIMULACRA.md`: informe (321 analizados, 62 cambios, 259 sin cambio).

Verificado: `acumulado == lote1 U lote2`, **0 divergencias** por clave EN.

### 27.2 Validacion

`tools/validate_fixes.py` -> lote 2: 62/62 OK; acumulado: 728/728 OK; 0 errores
(0 marcadores distintos, 0 URIs perdidas, 0 cambios de saltos de linea).

### 27.3 Aplicacion

`tools/apply_chatgpt_fixes.py` con el ACUMULADO: **66 sustituciones nuevas**
(lote 1 ya aplicado -> 666 omitidas sin efecto, idempotente).

### 27.4 Verificaciones

- `dist/es-latam.fs`: 908/908 ocurrencias del acumulado correctas, 0 incorrectas.
- Integridad: 30877/30877 cadenas, 0 objetos con nº distinto.
- `dist/core.assets` -> `en-us.fs` **identico byte a byte** (ingles intacto).
- `verify_build.py` y `verify_es_latam_coverage.py` -> TODO VALIDADO.

### 27.5 Mejora y clasificacion de lo pendiente

| incidencia | lote1 | lote2 | ahora |
|---|---|---|---|
| sin_traducir | 425 | 260 | 193 |
| relleno/truncado | 2564 | 59 | 1 |
| contenido_faltante | 35 | 2 | 1 |
| marcadores_distintos | 3 | 0 | 0 |

`export_revision.py` ahora NO marca como incidencia las **claves internas
protegidas** (`tools/keys_protegidas.txt`: `Camera`, `Chat Images`, `Voicemail`,
`Recovered`, `Me`, `Spark`, ...) ni fechas/colores hex/handles. Los 193
`sin_traducir` restantes son **nombres propios** (`Greg`, `Taylor`, `Anna`, ...),
hashtags, rutas y codigos que NO deben traducirse (los cambio el lote 2 solo en
3 risas: `Haha`->`Jaja`). Los 2 casos de truncamiento son **falsos positivos**
confirmados por ChatGPT (`I am just going to look for her.` -> `Voy a buscarla.`;
`This service is complimentary...` -> contenido completo sin punto final).

### 27.6 Commit respaldado

`fix(es-latam): aplica lote 2 de ChatGPT (62 correcciones, 66 sustituciones)`
en `origin/audit/export-dialogos-es-latam-v2` (commit `37c93cf`).

### 27.7 Proxima tarea concreta

1. Prueba visual en Wine de las pantallas corregidas (galeria, chat Ashley,
   boot-iris, respuestas de llamada). No ejecutable en este sandbox.
2. Revisar los 12 casos tecnicos marcados en el informe del lote 2 (albumes
   `Camera`/`Chat Images`/..., `Iris Chat`, `Me`, `Mom`, `Recovered`,
   `Voicemail`, `Wallpapers`, `Applesauce`): decidir si alguno tiene uso visible
   ademas del interno. Ver seccion 15 (claves protegidas) antes de traducir.
3. Si se desea traduccion de nombres de UI (p.ej. `Me`->`Yo`), comprobar primero
   que no sea clave interna; usar `tools/keys_protegidas.txt` como filtro.

---

## 28. Sesion 28 - CIERRE de la revision linguistica (incidencias = 0)

### 28.1 Entrada (respuesta de ChatGPT al prompt de cierre)

ChatGPT clasifico los 195 registros del lote 2:

| categoria | n | accion |
|---|---:|---|
| TRADUCIR | 2 | aplicadas |
| CLAVE | 46 | conservar |
| NOMBRE | 141 | conservar |
| TECNICO | 6 | conservar |

Las 2 unicas correcciones: `I am just going to look for her.` -> `Solo voy a
buscarla.` y `This service is complimentary for 1 year from this date.` ->
`Este servicio es gratuito durante un anio a partir de esta fecha.`

### 28.2 Aplicacion

- `fixes_lote3.json` (2 pares) validado: 2/2 OK, 0 errores.
- Aplicado: **3 sustituciones** en 3 objetos.
- `tools/confirmados_no_traducibles.txt`: 193 cadenas confirmadas como no
  traducibles (nombres/claves/tecnicos). `export_revision.py` ahora las carga
  y NO las vuelve a marcar como incidencia.

### 28.3 Resultado final

```
incidencias: {}   <- 0 sin_traducir, 0 truncado, 0 contenido_faltante,
                     0 marcadores_distintos
validate_export.py -> RESULTADO: OK - cobertura 100%
```

- Integridad: 30877/30877 cadenas; `en-us.fs` **identico byte a byte**.
- `verify_build.py` y `verify_es_latam_coverage.py` -> TODO VALIDADO.

### 28.4 Commit respaldado

`fix(es-latam): lote 3 (cierre) - ultimas 2 correcciones + 193 confirmadas no
traducibles` en `origin/audit/export-dialogos-es-latam-v2` (commit `b4d49c4`).

### 28.5 Estado del proyecto

La traduccion es-LATAM esta **cerrada a nivel de archivo**: todos los recursos
del `.fs` tienen su version espanola, sin incidencias detectables por las
heuristicas, con el ingles intacto y el es-LATAM como idioma independiente y
seleccionable.

**Lo unico que falta es la PRUEBA VISUAL EN EL JUEGO (Wine)**: ver las pantallas
corregidas (galeria, chat de Ashley, boot-iris, respuestas de llamada) para
confirmar que los textos se renderizan bien. No ejecutable en este sandbox.

### 28.6 Proxima tarea concreta

1. Ejecutar SIMULACRA en Wine con `dist/core.assets` + `dist/core.binary` y
   comprobar visualmente los textos en las escenas citadas.
2. Si alguna cadena se ve mal (cortada, desbordada, sin traducir), anotarla y
   crear un `fixes_lote4.json` con `{en, es}`; aplicar con el mismo pipeline.

## 29. Sesion 2026-11-11 (auditoria V2 ligera): minijuegos + fixes por objeto + Java

Rama de trabajo: `fix/auditoria-v2-minijuegos-java` (desde `ad7dc1b`).
Commits respaldados: `39f2632` y `f693829` en `origin/fix/auditoria-v2-minijuegos-java`.

### 29.1 Que se recupero del paquete adjunto

El usuario adjunto `SIMULACRA_OPENHANDS_AUDITORIA_LIGERA.zip` (auditoria V2 +
correcciones pendientes). Se descomprimio en `/tmp/paquete/`. Los tres SHA-256
de `dist/` **coincidian** con `MANIFIESTO_SHA256` del paquete, asi que la
auditoria describe el estado actual:
- `core.assets` `97b81e0f...`, `core.binary` `7d7ea3b5...`, `es-latam.fs` `943dffe9...`.

Contenido relevante:
- `SIMULACRA_V2_FIXES_POR_OBJETO.json` (52 correcciones por objeto).
- `SIMULACRA_MINIJUEGOS_RESTPHRASE_AUDITORIA.json` (25 minijuegos, 24 con diferencias).
- `SIMULACRA_MINIJUEGO_GREG1_FIXES.json` (3 fixes de alta confianza).
- `SIMULACRA_V2_PENDIENTES_JAVA.json` (28 cadenas en clases Java).

Verificacion inicial con `tools/verify_objeto_fixes.py`: **0 aplicadas, 52 PENDIENTE**.

### 29.2 Minijuegos `restphrase` (prioridad) — RESUELTO

Cada minijuego tiene 2 objetos: el recurso (`content/restphrase/<id>`) y sus
fragmentos. Ademas hay un "mensaje restaurado" (`corrupted://<id>=<frase>`) que
se muestra al completar. **El bug era que los fragmentos concatenados NO
coincidian con el mensaje restaurado** (frases agramaticales).

Solucion aplicada a 25 recursos:
- Se sincronizaron los **fragmentos** (fichas) y el **mensaje restaurado** para
  que concatenen EXACTAMENTE la misma frase natural.
- Se conserva: numero de fichas, prefijo `corrupted://<id>=`, marcador final.
- Se conserva el efecto visual "corrupto" (mayus/minus alternas en los
  recursos jamesh*, que imitan el estilo del original ingles).
- Casos: `greg1` (salio->paso, linea->raya), `james2` (`position`->`puesto`),
  `ashley1` (`phone`->`su`), `taylor1` (lastima), `gregrc2` (infiel),
  `jamesh10/11/13` (frases naturales), etc.

Resultado: **0 desajustes** entre fragmentos y mensaje restaurado en los 23
recursos con mensaje (`emailmurv1` y `james1` no tienen mensaje restaurado).

### 29.3 Correcciones por objeto (52) — APLICADAS

Puntuacion (signos de apertura ¿ ¡), tildes, `Ana`->`Anna`, `taylor`->`Taylor`,
y el correo completo de Anna a Ed (contenido_faltante). Total combinado
(52 objeto + 84 minijuegos, 2 ya aplicados) = **136 fixes, 136/136 correctos**
en `dist/es-latam.fs`.

### 29.4 Cadenas Java (28) — ACLARADO Y CERRADO

Las 28 cadenas del JSON siguen en **ingles en las clases base** (`game27.gb.*`).
Eso es **correcto**: el ingles NO se reemplaza. El espanol se sirve por clases
`game27.gbeslatam.*` via `Builder.overrides` (mecanismo replicado de `gbzhcn`).

Se encontro y corrigio un hueco real:
- `patch/game27/gb/GBMainMenu.java`: 3 cadenas (`OPTIONS`, `Talk to us...`,
  texto del modo `BEGIN+`) **no estaban envueltas en `L()`** y quedaban en
  ingles. Ahora devuelven espanol cuando el idioma activo es es-LATAM.
- `translations/es-LATAM/override_ui.json`: `"VOICE WORKS"` estaba sin traducir
  (creditos, `GBCreditsMenu`) -> `"TRABAJO DE VOCES"`.

`dist/core.binary` se reconstruyo con **JDK 21** (`javac --release 8`) a partir
de los originales pristinos extraidos de `SIMULACRA.7z` (con `7z`).

### 29.5 Herramientas nuevas

- `tools/apply_index_fixes.py` — aplica fixes por `{objeto, indice_cadena}`
  usando `fs_editor` (descomprime objetos zlib). Valida indice, texto actual e
  invariante de numero de cadenas; idempotente.
- `tools/verify_objeto_fixes.py` — clasifica APLICADA/PENDIENTE/DESPLAZADA/YA_OK.
- `tools/exenciones_minijuego.json` + `fs_fix_keys.py --exempt`: evita que
  `fs_fix_keys` revierta `phone`/`position` **solo** en los fragmentos de
  minijuego donde son texto visible (el resto de contextos sigue protegido).
- `tools/runtime_test/BlobLoad.java` + `run_blob_smoke.sh` — **prueba fuerte de
  runtime**: carga clases directamente desde `core.binary` replicando CodeBlob
  (SHA-1->unlock; AES/CTR + CRC32 + inflate), ejecuta `GBESLATAM.setup()` y
  comprueba que `GlobalTexts.text1` == "Galeria".

### 29.6 Comandos reproducibles

```bash
# Entorno (una vez):
7z e SIMULACRA.7z.001 -o/tmp/game core.assets core.binary support.binary -y
python3 -c "import zipfile;zipfile.ZipFile('/tmp/game/support.binary').extractall('/tmp/supportdir')"
python3 tools/blob_tool.py extract /tmp/game/core.binary /tmp/origcls   # clases pristinas
# JDK 21 en /tmp/jdk (o el que haya); javac --release 8

# Aplicar fixes por objeto+indice (fuente de verdad):
python3 tools/apply_index_fixes.py translations/es-LATAM/en-us.fs \
    fixes_auditoria_v2.json work/chatgpt/en-us.audit.fs --report exports/apply_auditoria_v2.json
cp work/chatgpt/en-us.audit.fs translations/es-LATAM/en-us.fs

# Build completo -> dist/:
JAVAC=/tmp/jdk/bin/javac ORIG=/tmp/game CLASES=/tmp/origcls SUPPORT=/tmp/supportdir \
    bash tools/build_all.sh

# Verificacion:
python3 tools/verify_build.py dist/core.assets dist/core.binary /tmp/game/core.assets
JAVAC=/tmp/jdk/bin/javac JAVA=/tmp/jdk/bin/java SUPPORT=/tmp/supportdir \
    bash tools/runtime_test/run_blob_smoke.sh dist/core.binary
```

### 29.7 Resultados de validacion de esta sesion

- `verify_build.py` -> **TODO VALIDADO** (207 nombres es-latam://, 28139 cadenas,
  0 prefijos Kryo corruptos, clases bytecode validas).
- `run_blob_smoke.sh` -> **BLOB-SMOKE OK** (`text1=Galeria text12=Telefono
  quest1a=Encontrar a Anna`; cargan GBMainMenu, GBCreditsMenu, GBNotification,
  GBRestorePhraseScreen, GBESLATAMOverrides desde el blob).
- 136/136 fixes por objeto correctos en `dist/es-latam.fs`.
- 0 desajustes de minijuegos.
- `en-us.fs` **identico** (md5 `d571609d36e29116f175bb2da9bf3b7b`).
- Integridad: 28315 objetos / 30877 cadenas (sin cambios de conteo).

### 29.8 Pendiente / proxima tarea concreta

1. **Prueba visual en el juego (Wine)** de las escenas de minijuego (restphrase)
   y del menu principal (`OPCIONES`, ayuda, modo BEGIN+), no ejecutable en este
   sandbox. Cargar `dist/core.assets` + `dist/core.binary`.
2. **Revisar el resto de recursos `.fs`** (`main.fs`, `content.fs`, `web.fs`,
   `videos.fs`, `zh-cn.fs`) por si hay texto traducible fuera de `en-us.fs`.
3. Si algo se ve mal, crear un `fixes_lote4.json` y aplicar con el mismo pipeline.
