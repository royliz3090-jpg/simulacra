# Descubrimientos de la auditoria (arquitectura interna de SIMULACRA)

Documento de trabajo para la extraccion exhaustiva (rama
`audit/export-dialogos-es-latam-v2`). Amplia `docs/ESTADO_TRADUCCION.md`.

## 1. Que es un `.fs`

Un miembro `*.fs` de `core.assets` (ZIP) es un "FileSystem" de Mass:

```
"FileSystem"          10 bytes
int32 field           field = (size << 1) | (compressed ? 1 : 0)
byte[size] format     bloque de formato (zlib o crudo)
byte[...]  data       bloque de datos (objetos serializados)
```

El bloque de **formato** descomprimido (ver `tools/build_locale_fs.parse_format`):

```
int32 total                       numero de objetos
int32[total] types                serializador de cada objeto (t&1 = comprimido)
int32[total] offsets              offset FINAL del objeto k dentro de data
int32[total] map_offsets          corte del array `map` por objeto
int32[...]   map                  grafo de referencias (ver abajo)
int32 serializersId               tabla id -> (nombre de clase, serializador)
int32 namesCount
{ string name; int32 id }         mapa nombre(URI) -> id de objeto
```

- `names` tiene **207 entradas** en `en-us.fs` y `es-latam.fs`; `name` es la URI
  (`en-us://content/chats/greg...` / `es-latam://...`) y `id` es el indice del
  objeto raiz de ese recurso.
- `types[k]` indexa la tabla `serializers` (p.ej. 27 = `DialogueTree$DialogueTreeDescriptor`).

## 2. El grafo `map` (clave para atribuir objetos a recursos)

`map` es un `int[]` concatenado. El corte del objeto `k` es
`[map_offsets[k-1], map_offsets[k])`. Cada valor `v` codifica una referencia:

```
indice_destino = v >> 2        (objeto referenciado)
tag            = v & 3         (3 = referencia normal; 0 = null/primitivo)
```

Se verifico que siguiendo las referencias con tag 3 (BFS) desde los 207 objetos
raiz se alcanzan **los 28315 objetos** del `.fs`; 27975 objetos tienen un unico
propietario (recurso raiz) y solo 340 tienen mas de uno (assets compartidos:
fuentes, texturas, animaciones). Esto permite atribuir cada mensaje a su
recurso (`content/chats/greg`, `content/mail/...`, etc.).

## 3. Donde vive el texto

El bloque de datos se escanea objeto por objeto. Un objeto es una secuencia de
valores Kryo/Mass; las cadenas van como `[u32 big-endian len][utf-8]`.

Dos escaneos distintos:

- **Escaneo de bloque completo** (`simulacra_fs.scan_strings` sobre todo `data`):
  28139 cadenas. Es el numero que usa el pipeline actual.
- **Escaneo por objeto** (descomprimiendo cada objeto antes de escanear):
  30877 cadenas = 27634 planas + 3243 dentro de objetos comprimidos con zlib.

**El escaneo por objeto es el exhaustivo.** El de bloque completo pierde las
3243 cadenas comprimidas y ademas inventa 490 falsos positivos de 1 caracter
(`x`, `>`, ...) que son bytes binarios que casualmente parecen `[00 00 00 01][x]`.
Conclusion: la cifra real de cadenas de texto es **30877**.

## 4. Objetos comprimidos

`types[k] & 1 == 1` -> el trozo de `data` esta comprimido con zlib (`78 da`).
En `es-latam.fs` hay **1746 objetos comprimidos** con 3243 cadenas. Suelen ser
arrays `[u32 count][str]...` o secuencias planas; en chats, la cola binaria tras
las cadenas guarda metadatos (`float`, etc.).

## 5. Formato de los mensajes de chat

`game27.model.ChatAppModel$ContactModel` (type 66, 3822 objetos) es un mensaje:

```
string <texto del mensaje>
string <remitente>       (p.ej. "sender", "auto", "you")
string <fecha>           ("01 August 2017")
string <hora>            ("10:30 AM")
[cola binaria]
```

El texto de restauracion corrupta aparece como
`corrupted://content/restphrase/greg1=<texto real>`.

## 6. Otros tipos relevantes

| type | clase | contenido |
|---|---|---|
| 27 | `DialogueTree$DialogueTreeDescriptor` | descriptor de arbol de dialogo |
| 28 | `[Lgame27.DialogueTree$Conversation;` | array de conversaciones |
| 31 | `[Lgame27.DialogueTree$UserMessage;` | respuestas del jugador |
| 32 | `[Lgame27.DialogueTree$SenderMessage;` | mensajes del personaje |
| 34 | `DialogueTree$UserMessage` | una respuesta del jugador |
| 33 | `DialogueTree$SenderMessage` | un mensaje del personaje |
| 60 | `RestorePhraseModel` | fichas de puzzles de restauracion |
| 66 | `ChatAppModel$ContactModel` | mensaje de chat |
| 76-80 | `DialogueTreeModel$*` | variante de modelo de dialogo |
| 85 | `FriendsAppModel$PostModel` | post de Jabbr |
| 14/17 | `SubtitleModel` / `$TextModel` | subtitulos |
| 18 | `WebpageModel` | pagina web |
| 26 | `LayoutModel$LayoutTextModel` | texto de layout |
| 26/54-56 | `LayoutDescriptor$Layout*` | texto/links de layout |
| 0 | `RestoreImageModel` | imagen de restauracion |
| 61 | `PhotoAppModel` | fotos/galeria |

## 7. Texto incrustado en clases Java (`core.binary`)

`core.binary` es un blob `KCB1` (AES-CTR + deflate; ver `tools/blob_tool.py`).
Contiene 1105 clases. Extrayendo desde `game27.DesktopMain` se recuperan 993
clases (`game27.*`, `sengine.*`, `bsh.*`).

- `game27/gb/GBENUS.class` = textos de UI en INGLES (238 cadenas LDC en `setup`).
- `game27/gbeslatam/GBESLATAM.class` = los mismos 238 textos en ESPANOL.
- Hay overrides es-LATAM en `game27/gbeslatam/**` (boot, browser, chats, friends,
  gallery, mail, phone, restore, spark, vloggr) que replican las clases
  `game27/gb/**`.

El orden de las cadenas LDC de `setup()` es **identico** entre EN y ES, lo que
permite emparejar texto UI original <-> traduccion actual por posicion.

Para leerlas hace falta un decodificador de bytecode (longitudes de operando +
`tableswitch`/`lookupswitch`); ver `tools/java_strings.py`.

## 8. Estado de traduccion (observado)

- Cadenas totales: 30877. Traducidas (ES != EN): ~6400. El resto son
  identificadores, rutas, fechas, nombres, emojis, shaders GLSL, etc.
- Firma de truncamiento: cadenas ES rellenadas con espacios finales para
  conservar la longitud en bytes del ingles (3249 casos). Muchas ya reparadas en
  sesiones previas.
- Los archivos `translations/es-LATAM/all_translations.json` y `work/*.json` son
  trabajo previo PARCIAL; no son fuente fiable (el propio encargo lo indica).
