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
- ✅ Archivos de traducción creados para los 207 URIs en `translations/es-LATAM/`
- ✅ Glosario creado (`GLOSSARY.md`)
- ✅ Script de extracción creado (`extract-simulacra-text.ps1`, `extract_text.py`)
- ✅ Scripts de instalación/desinstalación creados (`aplicar_parche.bat`, `desinstalar_parche.bat`)
- ✅ Instrucciones de instalación creadas (`INSTALL_ES.md`)

### 7.2 Bloqueo actual

**Extracción de texto real de objetos serializados Kryo/Java**

Los datos de texto reales están embebidos en objetos serializados con el framework Kryo/mass de Java dentro del índice URI→binario de `en-us.fs`. El archivo descomprimido contiene únicamente el índice (URI + puntero/offset + contador incremental), no los valores de string serializados. Los datos serializados no se encontraron en `core.binary`, `support.binary`, ni en otros archivos del juego.

Se intentó:
- Extracción de strings ASCII legibles del descomprimido: solo se encontraron nombres de clase, URIs y referencias técnicas (404 strings, 0 de diálogo)
- Búsqueda en `core.binary` (2.1 MB) y `support.binary` (20 MB): sin texto legible de diálogo
- Comparación con `zh-cn.fs`: sin caracteres CJK, todo en formato binario serializado
- Python 3.12 instalado para intentar parser Kryo: no se pudo localizar la sección de datos serializados

Se requiere:
1. Localizar dónde se almacenan los objetos serializados Kryo (posiblemente embebidos en el ejecutable o en un archivo no identificado)
2. Escribir un parser de serialización Kryo para extraer campos String
3. Reconstruir los árboles de diálogo completos

GameStringer no tiene parser para LibGDX/Kryo (soporta: Unity, Unreal, Godot, RPG Maker, Ren'Py, Bethesda, CRI Middleware, Telltale, Wolf RPG, Kirikiri, TyranoScript, Electron, Visionaire, Danganronpa — pero NO LibGDX/Java).

### 7.3 Próximos pasos

1. Localizar la sección de datos serializados Kryo en los archivos del juego
2. Escribir parser de serialización Kryo para extraer strings de DialogueTreeDescriptor
3. O alternativamente, usar OCR/GameStringer sobre capturas de pantalla del juego en ejecución
4. Traducir los 207 recursos identificados
5. Repacker los .fs con los textos traducidos
6. Ejecutar pruebas de validación del juego

## 8. Archivos de traducción creados

Directorio: `C:\IA-Prueba\SIMULACRA\translations\es-LATAM/`

| Subdirectorio | Contenido | Cantidad |
|---------------|-----------|----------|
| `dialogos/llamadas/` | Árboles de diálogo de llamadas telefónicas | 9 |
| `dialogos/chats/` | Árboles de diálogo de chats | 19 |
| `dialogos/correo/` | Árboles de diálogo de correo electrónico | 20 |
| `dialogos/spark/` | Árboles de diálogo de app Spark | 14 |
| `subtitulos/` | Subtítulos de audio y video | 68 |
| `web/` | Páginas web y layouts | 36 |
| `frases_restauracion/` | Frases de restauración de datos | 25 |
| `imagenes_restauracion/` | Imágenes de restauración | 7 |
| `configuracion/` | Archivos de configuración | 5 |
| `otro/` | Otros recursos | 4 |
| **Total** | **207 archivos de traducción** | **207 URIs** |

Cada archivo de traducción tiene el formato:
```json
{
  "uri": "en-us://content/chats/ashley.DialogueTreeDescriptor",
  "categoria": "chats",
  "texto_original": null,
  "texto_traducido": null,
  "estado": "pendiente_extraccion",
  "notas": "Texto no extraído: serialización Kryo/Java"
}
```

## 9. Limitaciones conocidas

- No se han extraído los textos completos de los diálogos (formato binario serializado Kryo)
- No se ha podido ejecutar el juego para validación visual (sin GPU, 8 GB RAM)
- GameStringer no soporta LibGDX nativamente
- Las texturas del menú con texto integrado requerirían edición de imagen o reemplazo de fuente
- Los archivos de traducción contienen plantillas con estado `pendiente_extraccion`

## 10. Referencias

- GameStringer docs/METODI-DI-TRADUZIONE.md — Registro de métodos de extracción por motor
- GameStringer docs/PATCH_SYSTEM.md — Sistema de gestión de parches
- GameStringer python-api/ — API de traducción con IA