# Guía Técnica: Extracción de Texto Kryo en SIMULACRA

## Problema

El texto de diálogo de SIMULACRA está almacenado en objetos serializados con **Kryo** (biblioteca de serialización Java) dentro del archivo `core.assets` → `en-us.fs`. El archivo descomprimido contiene únicamente un índice URI→metadatos, no los valores de string serializados.

## Estructura del archivo en-us.fs

### Formato LibGDX FileSystem

```
Offset 0-9:   "FileSystem" (magic, 10 bytes)
Offset 10-13: Cabecera interna (4 bytes)
Offset 14+:   Datos comprimidos con zlib (0x78 DA)
```

### Método de descompresión

```python
import zlib

data = open('en-us.fs', 'rb').read()
zlib_data = data[14:]  # Saltar cabecera FileSystem
raw_deflate = zlib_data[2:-4]  # Saltar header zlib (2 bytes) + Adler-32 (4 bytes)
decompressed = zlib.decompress(raw_deflate, -15)  # Raw deflate
```

### Estructura del índice descomprimido

El archivo descomprimido (512,026 bytes) contiene un índice puro:

```
[URI string]\x00\x00[bin2: 2 bytes][offset4: 4 bytes] [siguiente URI]...
```

Ejemplo de gap entre URIs:
```
00 00 60 63 00 00 00 22
 ^^^^  ^^^^  ^^^^^^^^^^
 ||||  ||||  |
 ||||  ||||  +-- offset4 (pequeño: 28-63, probablemente longitud o ID)
 ||||  |
 ||||  +-------- bin2 (apunta a tabla de offsets en el archivo)
 |
 +-------------- \x00\x00 (terminador de string + padding)
```

Los 207 URIs están ubicados aproximadamente en los bytes 500,000-503,700 del archivo descomprimido. No hay gaps grandes entre URIs que contengan datos serializados.

## Dónde está el texto real

El texto de diálogo real NO está en `en-us.fs`. También se buscó en:
- `core.binary` (2.1 MB, empieza con "KCB1" - Kryo Container Binary?) - sin texto legible
- `support.binary` (20 MB, es un ZIP con librerías Java) - sin texto del juego
- `simulacra.exe` (1.3 MB) - sin texto de diálogo
- `zh-cn.fs` (1.1 MB comprimido) - sin caracteres CJK legibles
- `main.fs`, `web.fs`, `content.fs`, `videos.fs` - solo referencias a sprites/texturas

**Conclusión:** Los objetos serializados Kryo con el texto de diálogo están almacenados en una ubicación no identificada, posiblemente:
1. Embebidos en `simulacra.exe` en formato comprimido/encriptado
2. En `core.binary` con un formato no identificado (KCB1)
3. En una sección del archivo `.fs` que no se ha podido localizar

## Pasos para completar la extracción

### Paso 1: Identificar la sección de datos serializados Kryo

Buscar en `core.binary` y `simulacra.exe` patrones de serialización Kryo:
- Magic de Java serialization: `AC ED 00 05`
- Patrones de varint de longitud + UTF-8
- Referencias a clases: `DialogueTreeDescriptor`, `DialogueNode`, `DialogueChoice`

### Paso 2: Escribir un deserializador Kryo

Necesitas:
1. Las definiciones de clase del juego (`DialogueTreeDescriptor`, `DialogueNode`, etc.)
2. La biblioteca Kryo con las clases registradas
3. Un parser que lea: class ID (varint) + campos del objeto

Ejemplo de estructura Kryo esperada:
```
[Class ID: varint]
  [Campo 1: tipo + valor]
  [Campo 2: tipo + valor]
  ...
[String: varint(longitud) + bytes UTF-8]
```

### Paso 3: Extraer y traducir los 207 recursos

Una vez extraído el texto, traducir cada URI a español latinoamericano usando los archivos en `translations/es-LATAM/`.

### Paso 4: Repacker los archivos .fs

Reemplazar los strings en inglés con los traducidos, manteniendo la estructura binaria.

## Archivos de traducción creados

Directorio: `translations/es-LATAM/`

Cada archivo JSON tiene el formato:
```json
{
  "uri": "en-us://content/chats/ashley.DialogueTreeDescriptor",
  "categoria": "chats",
  "texto_original": null,
  "texto_traducido": null,
  "estado": "pendiente_extraccion",
  "notas": "Texto no extraído: serialización Kryo/Java",
  "bin2": 25440,
  "bin2_hex": "0x6360",
  "offset4": 34,
  "offset4_hex": "0x00000022",
  "position": 500131
}
```

Categorías y cantidades:
| Categoría | URIs |
|-----------|------|
| subtitulos | 68 |
| web | 36 |
| chats | 19 |
| correo | 20 |
| spark | 14 |
| dialogo_llamadas | 9 |
| frases_restauracion | 25 |
| imagenes_restauracion | 7 |
| configuracion | 5 |
| otro | 4 |
| **Total** | **207** |

## Scripts incluidos

| Script | Descripción |
|--------|-------------|
| `extract-simulacra-text.ps1` | Extrae mapeo URI→binario de en-us.fs |
| `extract_text.py` | Parser Python para URIs y strings |
| `generate_translations.py` | Genera archivos de traducción JSON |
| `kryo_parser.py` | Parser de serialización Kryo (no encontró texto de diálogo) |
| `find_kryo_in_binary.py` | Busca strings Kryo en archivos .binary |
| `find_strings_binary.py` | Busca strings legibles en .binary |
| `find_strings_exe.py` | Busca texto en simulacra.exe |
| `aplicar_parche.bat` | Script de instalación del parche |
| `desinstalar_parche.bat` | Script de desinstalación |

## Limitaciones conocidas

1. **Texto de diálogo no extraído**: Los 207 recursos tienen `texto_original: null` y `estado: pendiente_extraccion`
2. **GameStringer no soporta LibGDX/Kryo**: Sus parsers cubren Unity, Unreal, Godot, RPG Maker, Ren'Py, Bethesda, CRI Middleware, Telltale, Wolf RPG, Kirikiri, TyranoScript, Electron, Visionaire, Danganronpa — pero NO LibGDX/Java
3. **No se pudo ejecutar el juego para validación**: Sin GPU, 8 GB RAM
4. **Texturas del menú con texto integrado**: Requieren edición de imagen o reemplazo de fuente

## Recursos externos

- ZenHAX forum: https://zenhax.com/viewtopic.php?t=13738 (discusión sobre extracción de .assets/.binary de SIMULACRA)
- GameStringer: https://github.com/rouges78/GameStringer (herramienta de traducción, no soporta LibGDX)
- LibGDX Kryo serialization: https://libgdx.com/wiki/utils/saved-game-serialization
- Kryo library: https://github.com/EsotericSoftware/kryo
