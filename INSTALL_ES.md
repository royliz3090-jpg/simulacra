# Instrucciones de Instalación y Desinstalación - Traducción SIMULACRA al español latinoamericano

## Requisitos previos

- Juego SIMULACRA instalado (versión original en inglés)
- Windows 10/11
- 7-Zip o similar para extraer archivos (opcional, para respaldo manual)

## Instalación

### Método 1: Aplicación automática de parche (recomendado)

1. Descarga el archivo de parche `SIMULACRA_es-LATAM_patch.zip`
2. Haz una copia de seguridad de tu carpeta del juego SIMULACRA
3. Ejecuta el script `aplicar_parche.bat` como administrador
4. El script:
   - Respalda los archivos originales (`core.assets.bak`, `support.assets.bak`)
   - Aplica los archivos traducidos en su lugar
   - Verifica la integridad de los archivos modificados
5. Inicia el juego y verifica que los textos aparezcan en español

### Método 2: Instalación manual

1. Haz una copia de seguridad de `core.assets` y `support.assets` en tu carpeta del juego
2. Copia los archivos traducidos desde `translations/es-LATAM/` a la carpeta del juego
3. Reemplaza `core.assets` con la versión traducida
4. Inicia el juego

### Ubicación de archivos del juego

Por defecto, SIMULACRA se instala en:
- Steam: `C:\Program Files (x86)\Steam\steamapps\common\SIMULACRA\`
- GOG: `C:\GOG Games\SIMULACRA\`
- Itch.io: Carpeta de instalación seleccionada durante la descarga

## Desinstalación

### Método 1: Script de desinstalación

1. Ejecuta `desinstalar_parche.bat` como administrador
2. El script restaurará los archivos originales desde las copias de seguridad
3. El juego volverá al inglés

### Método 2: Restauración manual

1. Elimina `core.assets` y `support.assets` traducidos
2. Renombra `core.assets.bak` a `core.assets`
3. Renombra `support.assets.bak` a `support.assets`

## Estructura del parche

```
SIMULACRA_es-LATAM_patch/
├── aplicar_parche.bat
├── desinstalar_parche.bat
├── core.assets          → Archivo de assets traducido
├── support.assets       → Archivo de assets traducido (si aplica)
├── translations/
│   └── es-LATAM/
│       ├── maestro.json
│       ├── dialogos/
│       │   ├── llamadas/
│       │   ├── chats/
│       │   ├── correo/
│       │   └── spark/
│       ├── subtitulos/
│       ├── web/
│       ├── frases_restauracion/
│       ├── imagenes_restauracion/
│       ├── configuracion/
│       └── otro/
├── GLOSSARY.md
├── TRANSLATION_REPORT.md
└── LICENSE
```

## Copias de seguridad

El instalador crea automáticamente copias de seguridad:
- `core.assets.bak` - Copia del archivo original
- `support.assets.bak` - Copia del archivo original (si se modifica)

Estos archivos se conservan para permitir la desinstalación.

## Limitaciones conocidas

- El texto de diálogo real está almacenado en formato de serialización binaria Kryo/Java
- Los archivos de traducción contienen plantillas (estado: `pendiente_extraccion`)
- Se requiere un parser específico de Kryo para extraer y traducir el texto completo
- Las texturas del menú con texto integrado no están traducidas (requieren edición de imagen)

## Soporte

Para reportar problemas o solicitar ayuda, consulta el archivo `TRANSLATION_REPORT.md`.
