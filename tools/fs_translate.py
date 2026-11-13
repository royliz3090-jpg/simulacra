#!/usr/bin/env python3
"""Busca posiciones de cadenas en un `.fs` y genera un fixes JSON.

Se usa para continuar traduciendo el `.fs` es-LATAM: localiza las cadenas que
siguen en ingles y emite un archivo apto para `tools/apply_fs_fixes.py`.

Uso:
  # 1) Listar candidatas sin traducir (identicas al ingles, no legitimas)
  python3 tools/fs_translate.py scan <es-latam.fs> <en-us-original.fs>

  # 2) Generar fixes para una lista de traducciones
  python3 tools/fs_translate.py fixes <es-latam.fs> <pares.json> <out.json>

`pares.json` es {"texto_ingles": "texto_espanol", ...}. Se sustituyen todas las
apariciones del ingles exacto.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulacra_fs as S  # noqa: E402
import verify_es_latam_coverage as V  # noqa: E402


def load(path):
    return open(path, "rb").read()


def strings_with_pos(raw):
    idx, off = S.split_fs(raw)
    return S.scan_strings(raw[off:])


def cmd_scan(es_path, en_path):
    es = strings_with_pos(load(es_path))
    en = strings_with_pos(load(en_path))
    seen = {}
    for i in range(min(len(es), len(en))):
        t, e = es[i]["text"], en[i]["text"]
        if t == e and not V.legit(t) and len(t) > 3:
            seen.setdefault(t, []).append(es[i]["pos"])
    print(f"{len(seen)} cadenas identicas al ingles no legitimas")
    for t in sorted(seen, key=lambda s: (-len(s), s)):
        print(f"  x{len(seen[t])}  {t!r}")


def cmd_fixes(es_path, pairs_path, out_path):
    es = strings_with_pos(load(es_path))
    pairs = json.load(open(pairs_path, encoding="utf-8"))
    fixes, found = [], {k: 0 for k in pairs}
    for x in es:
        t = x["text"]
        if t in pairs and pairs[t] and pairs[t] != t:
            fixes.append({"pos": x["pos"], "en": t, "es": pairs[t]})
            found[t] += 1
    json.dump(fixes, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"fixes escritos: {len(fixes)} en {out_path}")
    for k, n in found.items():
        if n == 0:
            print(f"  AVISO: sin apariciones: {k!r}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if sys.argv[1] == "scan":
        cmd_scan(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "fixes":
        cmd_fixes(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
