#!/usr/bin/env bash
# Prueba FUERTE de runtime: carga clases directamente desde core.binary
# replicando CodeBlob del juego (SHA-1 -> unlock; AES/CTR + CRC32 + inflate)
# y ejecuta GBESLATAM.setup(), comprobando que GlobalTexts queda en espanol.
#
# Uso: JAVAC=/tmp/jdk/bin/javac JAVA=/tmp/jdk/bin/java SUPPORT=/tmp/supportdir \
#        bash tools/runtime_test/run_blob_smoke.sh dist/core.binary
set -euo pipefail
cd "$(dirname "$0")/../.."
BIN="${1:-dist/core.binary}"
JAVAC="${JAVAC:-javac}"
JAVA="${JAVA:-java}"
SUPPORT="${SUPPORT:-/tmp/supportdir}"
TMP="$(mktemp -d)"
"$JAVAC" -nowarn -d "$TMP" tools/runtime_test/BlobLoad.java
"$JAVA" -cp "$TMP:$SUPPORT" BlobLoad "$BIN"
rm -rf "$TMP"
