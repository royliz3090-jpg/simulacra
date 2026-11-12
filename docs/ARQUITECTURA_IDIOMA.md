# Arquitectura de idioma de SIMULACRA (¡LÉEME PRIMERO!)

Este documento describe **cómo selecciona el juego su idioma**, hallazgo
obtenido por ingeniería inversa del código del juego. Es la base para añadir
el español latinoamericano como una opción **independiente y seleccionable**.

## 1. Dónde está el código del juego

El juego (LibGDX/Java) NO tiene las clases en un `.jar`. Las esconde en
`core.binary`, un blob propietario con formato **KCB1**:

```
core.binary
├── core.binary          -> blob KCB1 con las clases game27.*, sengine.*, bsh.*
├── support.binary       -> ZIP con librerías (gdx, lwjgl, etc.) + fuentes
├── core.assets          -> ZIP con los 7 recursos .fs (textos y datos)
├── support.assets       -> ZIP con texturas, sonidos, fuentes del juego
└── simulacra.exe        -> lanzador nativo (JVM embebida)
```

`simulacra.exe` -> `com.kaigan.game27.desktop.DesktopLauncher` carga
`core.binary` mediante `CodeBlob` (AES/CTR + deflate, clave = MD5(nombre de
clase)) y ejecuta `game27.DesktopMain`.

Ver `tools/blob_tool.py` para extraer/reempaquetar el blob desde Python
(no requiere Java).

## 2. Selección de idioma (¡el mecanismo clave!)

El idioma activo se guarda en las *preferences* de LibGDX bajo la clave
`STATE_LANGUAGE`, con un valor de "prefijo de contenido":

- `"en-us://"`  -> inglés
- `"zh-cn://"`  -> chino simplificado

`game27.Globals.contentPrefix` guarda ese prefijo.

`game27.Grid` (constructor) hace:

```java
Globals.contentPrefix =
    Gdx.app.getPreferences("preferences").getString("STATE_LANGUAGE", "en-us://");
boolean isEnglish = Globals.contentPrefix.equals("en-us://");
if (isEnglish) { GBENUS.setup(); } else { GBZHCN.setup(); }
```

`game27.Grid.load()` hace:

```java
if (Globals.contentPrefix.equals("en-us://")) { File.unpackFS("en-us.fs"); }
else                                          { File.unpackFS("zh-cn.fs"); }
```

`game27.Globals` define:

```java
public static final String CONTENT_PREFIX_EN_US = "en-us://";
public static final String CONTENT_PREFIX_ZH_CN = "zh-cn://";
public static final String STATE_LANGUAGE = "STATE_LANGUAGE";
```

## 3. Los paquetes "GB" (GameBook / UI por idioma)

Cada idioma tiene su propio paquete de pantallas y textos de interfaz:

- `game27.gb.*`       -> pantallas en **inglés** (`GBENUS`, `GBMainMenu`, ...)
- `game27.gbzhcn.*`   -> pantallas en **chino** (`GBZHCN`, ...)

`GBENUS.setup()` y `GBZHCN.setup()` hacen dos cosas:

1. Configuran `Globals` (nombre de guardado, locale de hora, etc.).
2. Rellenan `game27.GlobalTexts.text1..textN`, `quest1..quest60`, arrays de
   etiquetas, etc. con los textos de interfaz de ese idioma.

`GBZHCN.setup()` además registra las pantallas de UI específicas:

```java
Builder.overrides.put(game27.gb.GBScreenBar.class, game27.gbzhcn.GBScreenBar.class);
Builder.overrides.put(GBKeyboard.class, game27.gbzhcn.GBKeyboard.class);
// ... una por pantalla
```

`Builder.overrides` es un `HashMap<Class,Class>` que sustituye la clase de
layout por defecto por la de otro idioma (ver `sengine.utils.Builder`).

## 4. El selector de idioma en el menú

`game27.MainMenu` tiene un selector con botones **hardcodeados** para
inglés y chino (`languageEnglishButton`, `languageChineseButton`). Al pulsar:

```java
Globals.contentPrefix = "en-us://";   // o "zh-cn://"
Gdx.app.getPreferences("preferences").putString("STATE_LANGUAGE", Globals.contentPrefix).flush();
this.refreshLanguageStatus();
this.showLanguageMenu(true);
```

Al confirmar (botón OK) recarga el juego con `new Grid(false)`.

Los textos de ese menú provienen de `GlobalTexts` (definidos en el `.setup()`
del idioma), y los layouts de `game27.gb.GBMainMenu` (que a su vez tiene
textos incrustados como `"Are you sure you want to\nrestart ?"`).

## 5. Cómo añadir el español latinoamericano (plan)

Para que aparezca como opción **independiente** (sin reemplazar el inglés):

1. **Crear `es-latam.fs`** con el prefijo `es-latam://` y todas las cadenas
   traducidas. Se añade como miembro extra de `core.assets` (igual que
   `zh-cn.fs` convive con `en-us.fs`).
2. **Añadir la clase `game27.gbeslatam.GBESLATAM`** (análoga a `GBENUS`):
   - `Globals.contentPrefix` no se toca aquí (lo fija `Grid`).
   - Rellenar `GlobalTexts` en español.
   - Registrar `Builder.overrides` (reutilizando pantallas de `game27.gb.*`
     mientras no existan layouts propios en español).
3. **Parchear `game27.Globals`**: añadir `CONTENT_PREFIX_ES_LATAM = "es-latam://"`.
4. **Parchear `game27.Grid`**: rama de 3 vías en el constructor y en `load()`
   para reconocer `es-latam://` -> `GBESLATAM.setup()` + `File.unpackFS("es-latam.fs")`.
5. **Parchear `game27.MainMenu`**: añadir botón/etiqueta español y su handler.
6. **Reempaquetar `core.binary`** con las clases modificadas/nuevas.

### Nota sobre el trabajo previo (histórico)

El agente anterior (rama `feature/traduccion-es-latam`) intentó dos cosas:

- **Reemplazar** el contenido de `en-us.fs` por español (commit `f885822` y
  posteriores). Esto NO añade un idioma nuevo: cambia el inglés.
- Añadir un miembro `es-es.fs` extra al ZIP (commits `f885822`, `066ba340`)
  que era una **copia idéntica de `en-us.fs`** (sin integrar en el selector).

Ninguno de esos intentos integró el español en el selector nativo; el
selector es código Java dentro de `core.binary`. Por eso este documento
define el plan real.

## 6. Herramientas

| Herramienta | Función |
|-------------|---------|
| `tools/blob_tool.py` | Extraer/reempaquetar clases de `core.binary` (KCB1) desde Python |
| `tools/simulacra_fs.py` | Leer/modificar los `.fs` de `core.assets` |
| CFR (externo) | Descompilar clases a Java para entenderlas |

### Extraer las clases del juego

```bash
python3 tools/blob_tool.py info  /ruta/core.binary
python3 tools/blob_tool.py extract /ruta/core.binary /tmp/clases --roots game27.DesktopMain
python3 tools/blob_tool.py get   /ruta/core.binary game27.Grid /tmp/Grid.class
```

### Descompilar (necesita Java + CFR)

```bash
java -jar cfr.jar /tmp/clases/game27/Grid.class --outputdir /tmp/src
```

## 7. Estado de la verificación

- [x] Formato `core.binary` (KCB1) descifrado y documentado.
- [x] 951 clases extraídas (Python y Java coinciden byte a byte).
- [x] Mecanismo de idioma identificado (`STATE_LANGUAGE` -> `contentPrefix`
      -> `GBENUS`/`GBZHCN` -> `en-us.fs`/`zh-cn.fs`).
- [x] Selector nativo localizado en `game27.MainMenu`.
- [ ] `es-latam.fs` creado e integrado.
- [ ] `core.binary` parcheado con `GBESLATAM` y rama de 3 vías.
- [ ] Prueba real en el juego (requiere Windows/GPU; no disponible en sandbox).
