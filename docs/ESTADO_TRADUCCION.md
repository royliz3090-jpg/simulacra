# Estado de la traducción de SIMULACRA al español latinoamericano

> Documento persistente para continuar el trabajo desde cualquier sandbox.
> Última actualización: sesión de recuperación (ver sección "Último commit respaldado").

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

## 8. Trabajo recuperado vs. nuevo vs. pendiente

- **Recuperado**: `core.assets` v15b de `main` (6.024 cadenas traducidas), scripts de análisis,
  glosario y documentación previa de la rama `feature/traduccion-es-latam`.
- **Nuevo**: `tools/simulacra_fs.py`, esta documentación, catálogo de cadenas y listas de trabajo.
- **Pendiente**:
  - Reparar ~950 traducciones truncadas y nombres propios mal traducidos.
  - Traducir ~371 cadenas que siguen en inglés (subtítulos `vo://`, diálogos y menús).
  - Validación en el juego real (requiere Windows/GPU).

## 9. Último commit respaldado

Ver el historial de `feature/traduccion-es-latam-v2` en GitHub (el commit más reciente de esta rama
es el último respaldo). Base recuperada: `56e24e3` de `main`.

## 10. Próxima tarea concreta

1. Ejecutar `tools/simulacra_fs.py dump` sobre la base v15b y sobre el original.
2. Generar `traducciones.json` con: (a) correcciones de cadenas truncadas y nombres propios,
   (b) traducción de las cadenas que siguen en inglés.
3. Aplicar, verificar y commitear + push.
