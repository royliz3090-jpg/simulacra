#!/usr/bin/env python3
"""Rellena traducciones VACIAS (cadenas solo-espacios) en un `.fs`.

El en-us.fs pristino y la fuente espanola comparten la MISMA estructura de
objetos (mismo indice k). Dentro de cada objeto las cadenas planas se alinean
1:1 por orden. Donde el ingles tiene texto y el espanol solo espacios, se
sustituye por la traduccion del mapa (clave = texto ingles).

Entrada: JSON ``{"<texto en>": "<traduccion>"}``.

Uso:
  python3 tools/apply_empty_fixes.py <pristine_en.fs> <source_es.fs> <map.json> <out.fs>
"""
import json
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402


def obj_strings(body):
    """[(byte_offset_del_texto, texto)] de las cadenas planas de un objeto."""
    out, q, n = [], 0, len(body)
    while q + 4 <= n:
        L = struct.unpack_from(">I", body, q)[0]
        if L == 0 or L > 200000 or q + 4 + L > n:
            break
        try:
            out.append((q, body[q + 4:q + 4 + L].decode("utf-8")))
        except UnicodeDecodeError:
            break
        q += 4 + L
    return out


def main():
    en_fs, es_fs, map_json, out_fs = sys.argv[1:5]
    mp = json.load(open(map_json, encoding="utf-8"))

    _, en_objs = E.parse_fs(open(en_fs, "rb").read())
    f, es_objs = E.parse_fs(open(es_fs, "rb").read())

    applied = 0
    for k in range(min(len(en_objs), len(es_objs))):
        if es_objs[k]["comp"]:
            continue
        es = obj_strings(es_objs[k]["body"])
        en = obj_strings(en_objs[k]["body"])
        if len(en) != len(es):
            continue
        for (qe, te), (qs, ts) in zip(en, es):
            if not te.strip() or ts.strip():
                continue
            if te not in mp:
                continue
            body = es_objs[k]["body"]
            nb = mp[te].encode("utf-8")
            body[qs:qs + 4 + len(ts.encode("utf-8"))] = \
                struct.pack(">I", len(nb)) + nb
            applied += 1
            print(f"  obj{k}: [{te[:42]!r}] -> [{mp[te][:42]!r}]")

    open(out_fs, "wb").write(E.emit_fs(f, es_objs))
    print(f"rellenadas {applied} traducciones vacias")


if __name__ == "__main__":
    main()
