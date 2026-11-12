#!/usr/bin/env bash
# Construye un core.binary SOLO PARA PRUEBAS en sandbox (sin Steam).
#
# El core.binary de dist/ es para el juego real con Steam. En un entorno sin
# Steam (Wine, CI) el juego aborta con
#   "Unable to initialize steam and failed to restart".
# Este script reemplaza game27.DesktopMain por patch/test/DesktopMain.java
# (sin Steam, guardado local) y reempaqueta el blob.
#
# Requisitos:
#   - JDK 8+ (javac --release 8). Sandbox: /tmp/jdk-21.0.4+7/bin
#   - Clases del juego extraidas en CLASES (por defecto /tmp/pyclasses)
#     -> python3 tools/blob_tool.py extract <core.binary> CLASES
#   - Librerias (gdx, steamworks4j, ...) en SUPPORT.
#     Sandbox: extraer support.binary -> /tmp/supportdir
#     -> python3 -c "import zipfile;zipfile.ZipFile('support.binary').extractall('/tmp/supportdir')"
#
# Uso:
#   CLASES=/tmp/pyclasses SUPPORT=/tmp/supportdir \
#     bash tools/build_test_binary.sh dist/core.binary dist/core.test.binary
#
# Salida: blob con DesktopMain sin Steam (mismo resto de clases).
set -euo pipefail
cd "$(dirname "$0")/.."

IN_BIN="${1:-dist/core.binary}"
OUT_BIN="${2:-dist/core.test.binary}"
CLASES="${CLASES:-/tmp/pyclasses}"
SUPPORT="${SUPPORT:-/tmp/supportdir}"
JAVAC="${JAVAC:-/tmp/jdk-21.0.4+7/bin/javac}"
OUT=work/build/test

mkdir -p "$OUT/classes"
echo "[1/2] Compilando DesktopMain sin Steam (target Java 8)..."
"$JAVAC" --release 8 -nowarn -encoding UTF-8 \
  -cp "$CLASES:$SUPPORT" -d "$OUT/classes" patch/test/DesktopMain.java

echo "[2/2] Inyectando game27.DesktopMain en $OUT_BIN ..."
python3 tools/patch_core_binary.py "$IN_BIN" "$OUT_BIN" \
  --replace "game27.DesktopMain=$OUT/classes/game27/DesktopMain.class"

md5sum "$OUT_BIN"
echo "OK: binario de prueba sin Steam listo en $OUT_BIN"
