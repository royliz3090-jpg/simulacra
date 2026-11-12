# Instalación - Traducción de SIMULACRA al español latinoamericano (es-LATAM)

Este parche **añade** el español latinoamericano como un idioma **independiente y
seleccionable** en el juego. El inglés y el chino siguen disponibles; no se
reemplaza ningún idioma.

## Requisitos

- SIMULACRA instalado (Steam / GOG / itch.io), versión de escritorio (Windows).
- Windows 10/11.

## Instalación

### Método 1 - Script automático (recomendado)

1. Copia `aplicar_parche.bat`, `core.assets` y `core.binary` a una carpeta temporal.
2. Ejecuta `aplicar_parche.bat` **como administrador**.
3. El script:
   - Localiza la carpeta del juego.
   - Respalda `core.assets` y `core.binary` como `*.bak`.
   - Copia los archivos del parche sobre los originales.
4. Inicia el juego y elige el idioma (ver abajo).

### Método 2 - Manual

1. Haz copia de seguridad de `core.assets` y `core.binary` de tu carpeta del juego.
2. Copia `dist/core.assets` y `dist/core.binary` sobre los originales.
3. Inicia el juego.

### Ubicación habitual del juego

- Steam: `C:\Program Files (x86)\Steam\steamapps\common\SIMULACRA\`
- GOG: `C:\GOG Games\SIMULACRA\`
- itch.io: carpeta elegida al instalar.

## Cómo seleccionar el español

1. En el menú principal, abre **Idioma** (la bandera/opción de idioma).
2. Verás tres opciones: **English**, **中文** y **Español (Latinoamérica)**.
3. Elige **Español (Latinoamérica)** y pulsa el botón de confirmar.
4. El juego reinicia la carga de recursos y muestra todos los textos en español
   latinoamericano. La elección se guarda en las preferencias del juego.

## Desinstalación

### Método 1 - Script

1. Ejecuta `desinstalar_parche.bat` como administrador.
2. Restaura `core.assets` y `core.binary` desde las copias `.bak`.

### Método 2 - Manual

1. Renombra `core.assets.bak` -> `core.assets` y `core.binary.bak` -> `core.binary`.

## Qué contiene el parche

```
dist/
├── core.assets    # ZIP con los recursos originales + es-latam.fs (texto es-LATAM)
└── core.binary    # Blob de clases Java: añade game27.gbeslatam.GBESLATAM y
                   # habilita la tercera opción de idioma en el menú
```

El recurso de idioma `es-latam.fs` se construye a partir de
`translations/es-LATAM/en-us.fs` (texto es-LATAM) reescribiendo el prefijo del
índice de `en-us://` a `es-latam://`.

## Limitaciones conocidas

- Las texturas del menú con texto incrustado en la imagen no se traducen.
- Las voces originales están en inglés; los subtítulos sí están traducidos.
- Si el juego se congela al cargar, verifica que copiaste **ambos** archivos
  (`core.assets` y `core.binary`).

## Verificación técnica (sin ejecutar el juego)

```bash
python3 tools/verify_build.py dist/core.assets dist/core.binary /tmp/game/core.assets
```

Debe terminar con `TODO VALIDADO`.
