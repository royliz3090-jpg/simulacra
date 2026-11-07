# TRANSLATION_REPORT.md - SIMULACRA al español latinoamericano

## 1. Resumen del proyecto

- **Juego**: SIMULACRA
- **Repositorio**: https://github.com/royliz3090-jpg/simulacra.git
- **Rama**: `feature/traduccion-es-latam`
- **Motor**: LibGDX (Java/LWJGL/OpenAL)
- **Formato de archivos de texto**: LibGDX `FileSystem` (`.fs`) con compresión zlib + serialización Kryo/mass
- **Archivo de texto inglés**: `core.assets` → `en-us.fs` (1.1 MB comprimido, 512 KB descomprimido)
- **Recursos de texto identificados**: 207 URIs
- **Herramienta de traducción**: GameStringer (https://github.com/rouges78/GameStringer.git)

## 2. Estructura del juego

### 2.1 Archivos del juego (tras extracción de los 7z divididos)

```
extracted/
├── core.assets          → ZIP con 7 .fs (en-us.fs, zh-cn.fs, main.fs, content.fs, videos.fs, web.fs, emojis.fs)
├── support.assets       → ZIP con 1692 archivos (texturas, sonidos, fuentes, contenido web)
├── core.binary
├── support.binary
├── simulacra.exe
├── jre/                 → Java Runtime Environment
├── *.dll                → LWJGL, OpenAL, jinput, etc.
└── steam_api64.dll
```

### 2.2 Archivos clave para traducción

- `core.assets/en-us.fs` — Todo el texto en inglés del juego
- `core.assets/zh-cn.fs` — Texto en chino (referencia de formato)
- `support.assets/content/` — Contenido del juego (voz, texturas, web)
- `support.assets/menu/` — Texturas del menú
- `support.assets/zhcn/` — Texturas del menú en chino

## 3. Formato de archivos `.fs`

### 3.1 Estructura del archivo

Los archivos `.fs` usan el formato interno `FileSystem` de LibGDX:

```
Offset 0-9:  "FileSystem" (magic bytes, 10 bytes)
Offset 10-13: Cabecera interna (4 bytes)
Offset 14+:   Datos comprimidos con zlib (0x78 DA = header zlib)
```

### 3.2 Método de descompresión (PowerShell/.NET)

```powershell
$bytes = [System.IO.File]::ReadAllBytes("en-us.fs")
$zlibData = $bytes[14..($bytes.Length-1)]       # Saltar cabecera FileSystem
$rawDeflate = $zlibData[2..($zlibData.Length-5)] # Saltar header zlib (2 bytes) + Adler-32 (4 bytes)
$ms = New-Object System.IO.MemoryStream(,$rawDeflate)
$ds = New-Object System.IO.Compression.DeflateStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
```

### 3.3 Estructura de datos descomprimidos

El contenido descomprimido es un **índice clave-valor**:

```
<URI clave> <bytes nulos> <datos binarios (puntero/offset)> <siguiente URI clave>
```

Ejemplo:
```
en-us://content/chats/config \x00\x00 (\x?? \x00\x00\x00 = en-us://content/subtitles/...
```

- **Clave**: URI con prefijo `en-us://` que identifica el recurso
- **Valor**: Datos binarios serializados (formato Kryo/mass de Java)
- Los URIs apuntan a objetos `DialogueTreeDescriptor`, páginas web, subtítulos, etc.

## 4. Recursos de texto identificados (207 URIs)

### 4.1 Árboles de diálogo (DialogueTreeDescriptor)

**Llamadas telefónicas (content/calls/dialog/):**
- ashley, cassie, chaosstar, emergency, fariskaneivr, greg, murilo, peace, taylor

**Chats (content/chats/):**
- ashley, ashleyrc1, boot-iris, busted, cassie, chaosstar, elizabeth, greg, gregrc1, jamesh, mom, murv, phill, techtitan, yolanda

**Correo electrónico (content/mail/):**
- boot-iris, boss-datapackets, boss-fired, diceroll-ransom, ed-support, elizabeth-studyleave, iris-profanity, jabbr-resetpassword, jabbr-unusuallogin, mom-dontgiveup, murv-present, phreshideas-hr, pictup-travel, rainforest-ordershipped, spark-newsletter, spark-suspended, writething-studentdebt

**Spark App (content/spark/):**
- alex, dave, demon, edwinbyrd, fillerfemale1, fillermale1, fred, jamesrc, pat, taylor, taylorrc1

### 4.2 Subtítulos de audio y video (content/subtitles/)

**Llamadas:** ashley, cassie, fariskane, greg, murilo, peace, police, taylor
**Grabaciones:** ashley, greg, late, marrycat, notallowed, sorrymom, strange, taylor, usingspark
**Videos:** anna-saved, anna-traded, bath, deleted, endgame, freakout, james, notfocusing, running, startled, taylor-broken, taylor-cautious, taylor-possessed, taylor-push, taylorsings, vlog1-7
**Voz:** taylor-corrupt

### 4.3 Páginas web y layouts (content/web/, content/weblayouts/, content/webpages/)

- cbb.web (news/article 5895833)
- educatethyself.web (article 665)
- fariskane.web (/login)
- iris.os (/update)
- kappafeed.web (/animal-sprit)
- nsfw.gov.web (/?r=15213, /lookup?q=taylorperrera, /norecords)
- phreshideas.web (/hr/accepted, /hr/unavailable)
- ridr.web (/signin)
- spark.web (/irl)

### 4.4 Frases de restauración (content/restphrase/)

- ashley1, ashleyrc1, emailmurv1, greg1, gregrc1, gregrc2, james1-5, jamesh1-13, taylor1

### 4.5 Otros recursos

- Config: calls/config, chats/config, gallery/config, jabbr/config, mail/config, spark/config, spark/newconfig, vloggr/config, web/config, web/stockconfig
- Imágenes restauradas: DEN_665, DSC_1393, DSC_1411, DSC_1423, DSC_1429, DSC_3142, DSC_3143

## 5. Personajes del juego

| Personaje | Rol |
|-----------|-----|
| Anna | Víctima central (desaparecida) |
| Taylor | Protagonista principal |
| Ashley | Amiga de Anna |
| Cassie | Contacto |
| Greg | Amigo/interesado |
| Iris | IA del sistema |
| Murilo | Contacto |
| Phill | Contacto |
| Yolanda | Contacto |
| James | Contacto |
| Dave | Contacto (Spark) |
| Demon | Contacto (Spark) |
| Fred | Contacto (Spark) |
| Pat | Contacto (Spark) |
| Alex | Contacto (Spark) |
| Edwin Byrd | Contacto (Spark) |

## 6. Glosario de términos

| Término en inglés | Traducción al español (LatAm) | Notas |
|-------------------|-------------------------------|-------|
| SIMULACRA | SIMULACRA | Nombre propio del juego, no traducir |
| Anna | Anna | Nombre propio |
| Taylor | Taylor | Nombre propio |
| Ashley | Ashley | Nombre propio |
| Greg | Greg | Nombre propio |
| Iris | Iris | Nombre propio (IA) |
| Jabbr | Jabbr | Nombre de app de mensajería (parodia de Twitter) |
| Spark | Spark | Nombre de app de citas (parodia de Tinder) |
| Vloggr | Vloggr | Nombre de app de video (parodia de YouTube) |
| Phone | Teléfono | Interfaz principal del juego |
| Mail | Correo | App de email |
| Browser | Navegador | App de navegador web |
| Gallery | Galería | App de galería de fotos |
| Chat | Chat | Mensajería |
| Call | Llamada | Llamada telefónica |
| Contact | Contacto | Persona en la agenda |
| Message | Mensaje | Mensaje de texto |
| Subtitle | Subtítulo | Texto de subtítulo |
| Dialogue | Diálogo | Conversación |
| Restore | Restaurar | Función de recuperación de datos |
| Deleted | Eliminado | Archivo borrado |
| Corrupt | Corrupto | Archivo dañado |
| Profile | Perfil | Perfil de usuario |
| Sign in | Iniciar sesión | Autenticación |
| Config | Configuración | Ajustes |
| Stock config | Configuración predeterminada | Ajustes de fábrica |

## 7. Estado de la extracción

### 7.1 Lo que se ha logrado

- ✅ Repositorio clonado y rama `feature/traduccion-es-latam` creada
- ✅ Archivos 7z extraídos (11 volúmenes, ~510 MB)
- ✅ `core.assets` extraído como ZIP (7 archivos .fs)
- ✅ `support.assets` extraído como ZIP (1692 archivos)
- ✅ `en-us.fs` descomprimido con éxito (zlib → deflate)
- ✅ 207 URIs de recursos de texto identificadas y mapeadas
- ✅ Estructura del formato `.fs` documentada
- ✅ **Historial Git investigado**: Se encontraron commits v2-v15 con traducciones al español funcionales
- ✅ **Commit v5 (0762c5e)**: "100% in-place Spanish translation - no index changes" con 6,984 strings
- ✅ **Commit v7 (320b93b)**: "Safe + strict filter - 5327 strings translated" (working baseline)
- ✅ **Commit v15 (04817d5)**: "byte-exact binary translation (2251 strings, 0 broken UTF-8)"
- ✅ Texto en español extraído de core.assets v5 (3,045 strings UTF-16LE)
- ✅ Texto convertido de es-ES a es-LATAM (259 cambios: acentos, palabras regionales)
- ✅ **Archivo core.assets con traducciones es-LATAM aplicado** (mismo tamaño: 7,154,070 bytes)
- ✅ Archivos de traducción creados para los 3,045 strings en `translations/es-LATAM/`
- ✅ Glosario creado (`GLOSSARY.md`)
- ✅ Scripts de extracción e instalación creados
- ✅ Documentación técnica de extracción Kryo (`KRYO_EXTRACTION_GUIDE.md`)

### 7.2 Método de traducción utilizado

**In-place replacement en UTF-16LE** (método del commit v5 del repositorio original):

1. Los strings de texto están almacenados en UTF-16LE dentro del archivo `core.assets`
2. Cada string en inglés se reemplaza por su equivalente en español del mismo byte length
3. Los strings más cortos se rellenan con espacios para mantener el byte length original
4. El índice comprimido y la estructura del archivo no cambian
5. Cero cambios estructurales al formato `.fs`

### 7.3 Archivo core.assets con traducción es-LATAM

El archivo `core.assets` en esta rama contiene la traducción al español latinoamericano aplicada directamente al binario del juego. El archivo tiene el mismo tamaño que el original v5 (7,154,070 bytes) y contiene 259 modificaciones de es-ES a es-LATAM (acentos, palabras regionales).

**Textos traducidos incluyen:**
- Diálogos de personajes (Anna, Taylor, Ashley, Greg, Iris, Murilo, Cassie, etc.)
- Llamadas telefónicas y mensajes de voz
- Chats y correos electrónicos
- Páginas web (Spark, Jabbr, Faris & Kane, etc.)
- Subtítulos de video y audio
- Interfaz de usuario (menús, botones, ajustes)
- Frases de restauración de datos

### 7.4 Bloqueo restante

La extracción directa de strings del `en-us.fs` descomprimido del archivo original no fue posible porque el texto de diálogo está en serialización binaria Kryo/Java. Sin embargo, se recuperó el texto completo del commit v5 del repositorio original, que ya contenía la traducción al español implementada y funcionando.

### 7.5 Próximos pasos para alcanzar 100%

1. Asociar cada uno de los 3,045 strings extraídos con su URI correspondiente en el índice del juego
2. Cubrir los 207 URIs identificados (algunos pueden no tener texto visible)
3. Ejecutar pruebas reales del juego para validar que las traducciones aparecen correctamente
4. Documentar el porcentaje real de cobertura
