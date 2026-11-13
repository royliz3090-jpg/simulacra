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

echo "[1/6] Generando clases de UI en espanol (Builder.overrides)..."
# Textos de UI "hardcodeados" en las clases gb.* : el juego los cambia por
# clases especificas del idioma (game27.gbzhcn.* para zh-cn). Replicamos el
# mecanismo para es-LATAM reescribiendo las cadenas de la clase base y
# renombrandola a game27.gbeslatam.*. Se excluye GBMainMenu: ese lo parcheamos
# a mano (selector de idioma + textos dinamicos).
rm -rf "$OUT/overrides"
python3 tools/gen_es_overrides.py "$CLASES" "$OUT/overrides" \
  --exclude GBMainMenu \
  --java-out patch/game27/gbeslatam/GBESLATAMOverrides.java

echo "[2/6] Compilando clases parcheadas (target Java 8)..."
rm -rf "$OUT/classes" && mkdir -p "$OUT/classes"
"$JAVAC" --release 8 -nowarn -encoding UTF-8 \
  -cp "$CLASES:$SUPPORT:$OUT/overrides" -d "$OUT/classes" \
  patch/game27/Globals.java patch/game27/Grid.java patch/game27/MainMenu.java \
  patch/game27/gb/GBMainMenu.java patch/game27/gbeslatam/GBESLATAM.java \
  patch/game27/gbeslatam/GBESLATAMKeyboard.java \
  patch/game27/gbeslatam/GBESLATAMOverrides.java

echo "[3/6] Construyendo es-latam.fs a partir del .fs traducido..."
# Fuente de verdad del texto es-LATAM: translations/es-LATAM/en-us.fs
# (contenido espanol en el espacio de nombres en-us://).
#
# ANTES de reescribir el prefijo hay que restaurar las CLAVES internas del
# juego (nombres de album como _Jabbr/cover, valores como missed/incoming/
# vlog3/center...) y las FECHAS serializadas: si se traducen, el juego falla
# al cargar ("Unable to find media _Jabbr/cover", "Failed to parse time...").
# El .fs original en ingles es la referencia del orden de cadenas.
python3 tools/fs_fix_keys.py "$ORIG/core.assets" translations/es-LATAM/en-us.fs \
  "$OUT/en-us.fixed.fs" --keys tools/keys_protegidas.txt >/dev/null
# NOTA: $ORIG/core.assets es un ZIP; fs_fix_keys lee su miembro en-us.fs.
python3 tools/build_locale_fs.py "$OUT/en-us.fixed.fs" x "$OUT/es-latam.fs" \
  --old-prefix en-us:// --new-prefix es-latam:// --direct >/dev/null

echo "[4/6] Ensamblando core.assets (ingles restaurado + es-latam.fs)..."
python3 tools/build_core_assets.py "$ORIG/core.assets" "$OUT/core.assets" \
  --add es-latam.fs="$OUT/es-latam.fs"

echo "[5/6] Empaquetando core.binary (familias completas + clases nuevas)..."
# IMPORTANTE: hay que reemplazar la familia COMPLETA de cada clase parcheada.
# Si solo se reemplaza la clase externa (p.ej. game27.MainMenu) pero no su
# clase interna (game27.MainMenu$Internal), la interna antigua no tendra los
# campos nuevos y el juego fallara con NoSuchFieldError.
REPLACE_ARGS=()
for rel in \
  game27/Globals game27/Globals\$Achievement \
  game27/Grid game27/Grid\$1 game27/Grid\$EvalTrigger \
  game27/Grid\$ScheduledRunnable game27/Grid\$ScreenCompositor game27/Grid\$Trigger \
  game27/MainMenu game27/MainMenu\$1 game27/MainMenu\$2 game27/MainMenu\$3 \
  game27/MainMenu\$Internal game27/MainMenu\$MusicFadeOutEntity \
  game27/MainMenu\$Particle game27/MainMenu\$ParticleType \
  game27/gb/GBMainMenu ; do
  cls="${rel//\//.}"
  REPLACE_ARGS+=(--replace "$cls=$OUT/classes/$rel.class")
done
# Clases NUEVAS: GBESLATAM + GBESLATAMOverrides + todas las UI game27.gbeslatam.*
ADD_ARGS=(
  --add game27.gbeslatam.GBESLATAM="$OUT/classes/game27/gbeslatam/GBESLATAM.class"
  --add game27.gbeslatam.GBESLATAMOverrides="$OUT/classes/game27/gbeslatam/GBESLATAMOverrides.class"
  --add game27.gbeslatam.GBESLATAMKeyboard="$OUT/classes/game27/gbeslatam/GBESLATAMKeyboard.class"
)
while IFS= read -r cls; do
  rel="${cls#$OUT/overrides/}"
  fqn="${rel%.class}"; fqn="${fqn//\//.}"
  ADD_ARGS+=(--add "$fqn=$cls")
done < <(find "$OUT/overrides" -name '*.class')
python3 tools/patch_core_binary.py "$ORIG/core.binary" "$OUT/core.binary" \
  "${REPLACE_ARGS[@]}" "${ADD_ARGS[@]}"

echo "[6/6] Copiando a dist/..."
cp "$OUT/core.assets" dist/core.assets
cp "$OUT/core.binary" dist/core.binary
cp "$OUT/es-latam.fs" dist/es-latam.fs
md5sum dist/core.assets dist/core.binary dist/es-latam.fs
echo "OK: entregables listos en dist/"
