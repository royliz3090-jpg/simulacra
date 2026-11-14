#!/usr/bin/env bash
# Reconstruye es-latam.fs + dist/core.assets SIN Java (los dialogos viven en el
# .fs; core.binary no cambia).
#
# Uso: bash tools/rebuild_es.sh
#
# Requiere el en-us.fs INGLES pristino como referencia de orden de cadenas.
# Fuente de verdad: translations/es-LATAM/en-us.fs (espanol, mismo orden).
set -euo pipefail
cd "$(dirname "$0")/.."

SRC=translations/es-LATAM/en-us.fs
OUT=work/build
mkdir -p "$OUT" dist

echo "[1/5] Extrayendo en-us.fs pristino de dist/core.assets..."
python3 - <<'PY'
import zipfile
z = zipfile.ZipFile('dist/core.assets')
open('/tmp/en-orig.fs', 'wb').write(z.read('en-us.fs'))
print('  /tmp/en-orig.fs OK')
PY

echo "[2/5] Restaurando claves protegidas + fechas (fs_fix_keys)..."
python3 tools/fs_fix_keys.py /tmp/en-orig.fs "$SRC" "$OUT/en-us.fixed.fs" \
  --keys tools/keys_protegidas.txt \
  --exempt tools/exenciones_minijuego.json >/dev/null

echo "[3/5] Reescritura de prefijo en-us:// -> es-latam://..."
python3 tools/build_locale_fs.py "$OUT/en-us.fixed.fs" x "$OUT/es-latam.fs" \
  --old-prefix en-us:// --new-prefix es-latam:// --direct >/dev/null

echo "[4/5] Ensamblando core.assets (ingles pristino + es-latam.fs)..."
# dist/core.assets ya trae es-latam.fs: hay que REEMPLAZARLO, no anadirlo
# (si se anade, el ZIP queda con dos entradas del mismo nombre).
python3 tools/build_core_assets.py dist/core.assets "$OUT/core.assets" \
  --replace en-us.fs=/tmp/en-orig.fs \
  --replace es-latam.fs="$OUT/es-latam.fs"

echo "[5/5] Copiando a dist/..."
cp "$OUT/core.assets" dist/core.assets
cp "$OUT/es-latam.fs" dist/es-latam.fs
md5sum dist/core.assets dist/es-latam.fs
echo "OK: entregables es-LATAM reconstruidos (sin Java)."
