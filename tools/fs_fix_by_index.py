#!/usr/bin/env python3
"""Genera fixes {pos,en,es} para cadenas del `.fs` identificadas por indice.

Util cuando el texto actual lleva relleno de espacios (truncamiento in-place) y
por tanto no se puede emparejar por texto exacto con `fs_translate.py fixes`.

Uso:
  python3 tools/fs_fix_by_index.py <es-latam.fs> <index_map.json> <out.json>

`index_map.json` es {"<indice>": "texto espanol completo", ...}.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulacra_fs as S  # noqa: E402


def main():
    fs_path, map_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(fs_path, "rb").read()
    idx, off = S.split_fs(raw)
    items = S.scan_strings(raw[off:])
    mapping = json.load(open(map_path, encoding="utf-8"))
    fixes = []
    for k, es in mapping.items():
        i = int(k)
        if i >= len(items):
            print(f"AVISO: indice fuera de rango: {i}")
            continue
        cur = items[i]["text"]
        if cur.strip() == es:
            continue
        fixes.append({"pos": items[i]["pos"], "en": cur, "es": es})
    json.dump(fixes, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"fixes escritos: {len(fixes)} en {out_path}")
    for f in fixes:
        print(f"  [{f['en'][:45]!r}] -> {f['es'][:60]!r}")


if __name__ == "__main__":
    main()
