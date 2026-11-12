#!/usr/bin/env bash
# Pipeline reproducible: fuente -> entregables del parche es-LATAM.
#
# Requisitos:
#   - JDK 8+ (javac con --release 8). En el sandbox: /tmp/jdk-21.0.4+7/bin
#   - Clases originales del juego extraidas en CLASES (por defecto /tmp/pyclasses)
#     -> python3 tools/blob_tool.py extract core.binary CLASES
#   - Librerias de support.binary en SUPPORT (por defecto /tmp/support.jar)
#   - Copia limpia (ingles) de core.assets y core.binary en ORIG
#
# Uso:
#   ORIG=/tmp/game CLASES=/tmp/pyclasses SUPPORT=/tmp/support.jar \
#     bash tools/build_all.sh
#
# Salidas en dist/: core.assets, core.binary, es-latam.fs
set -euo pipefail
cd "$(dirname "$0")/.."

ORIG="${ORIG:-/tmp/game}"
CLASES="${CLASES:-/tmp/pyclasses}"
SUPPORT="${SUPPORT:-/tmp/support.jar}"
JAVAC="${JAVAC:-/tmp/jdk-21.0.4+7/bin/javac}"
OUT=work/build
mkdir -p "$OUT" dist

echo "[1/5] Compilando clases parcheadas (target Java 8)..."
rm -rf "$OUT/classes" && mkdir -p "$OUT/classes"
"$JAVAC" --release 8 -nowarn -encoding UTF-8 \
  -cp "$CLASES:$SUPPORT" -d "$OUT/classes" \
  patch/game27/Globals.java patch/game27/Grid.java patch/game27/MainMenu.java \
  patch/game27/gb/GBMainMenu.java patch/game27/gbeslatam/GBESLATAM.java

echo "[2/5] Construyendo es-latam.fs a partir del .fs traducido..."
# El contenido traducido vive en core.assets (en-us.fs con textos es-LATAM).
# Se reescribe su prefijo a es-latam:// conservando el bloque de datos.
python3 tools/build_locale_fs.py core.assets en-us.fs "$OUT/es-latam.fs" \
  --old-prefix en-us:// --new-prefix es-latam:// >/dev/null

echo "[3/5] Ensamblando core.assets (ingles restaurado + es-latam.fs)..."
python3 tools/build_core_assets.py "$ORIG/core.assets" "$OUT/core.assets" \
  --add es-latam.fs="$OUT/es-latam.fs"

echo "[4/5] Empaquetando core.binary (4 reemplazos + 1 clase nueva)..."
python3 tools/patch_core_binary.py "$ORIG/core.binary" "$OUT/core.binary" \
  --replace game27.Globals="$OUT/classes/game27/Globals.class" \
  --replace game27.Grid="$OUT/classes/game27/Grid.class" \
  --replace game27.MainMenu="$OUT/classes/game27/MainMenu.class" \
  --replace game27.gb.GBMainMenu="$OUT/classes/game27/gb/GBMainMenu.class" \
  --add game27.gbeslatam.GBESLATAM="$OUT/classes/game27/gbeslatam/GBESLATAM.class"

echo "[5/5] Copiando a dist/..."
cp "$OUT/core.assets" dist/core.assets
cp "$OUT/core.binary" dist/core.binary
cp "$OUT/es-latam.fs" dist/es-latam.fs
md5sum dist/core.assets dist/core.binary dist/es-latam.fs
echo "OK: entregables listos en dist/"
