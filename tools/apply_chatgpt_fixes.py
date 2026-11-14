#!/usr/bin/env python3
"""Aplica correcciones linguiticas {en, es} de ChatGPT al `.fs` de traduccion.

`fixes.json` (salida de ChatGPT) es una lista ``[{"en": <ingles>, "es": <nuevo
espanol>}]``. La clave ``en`` identifica la CADENA por su texto INGLES, no el
espanol actual (que puede estar truncado). Por tanto:

  1. Se localiza cada ``en`` en el `.fs` INGLES (mismo orden objeto/ordinal que
     la traduccion: alineacion verificada, 0 diferencias).
  2. Se obtiene la posicion de la cadena espanola correspondiente en el `.fs`
     de traduccion (mismo objeto + mismo ordinal).
  3. Se sustituye esa cadena por el ``es`` propuesto, reescribiendo el objeto.

Funciona igual con objetos planos y comprimidos (zlib): `fs_editor` descomprime
al parsear y recomprime al emitir, recalculando los offsets.

Uso:
  python3 tools/apply_chatgpt_fixes.py <en.fs> <es.fs> <fixes.json> <out.fs>
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402
import simulacra_fs as S  # noqa: E402


def scan_objects(objs):
    """[[{pos,text}...] por objeto] usando el escaner canonico."""
    return [S.scan_strings(bytes(o["body"])) for o in objs]


def main():
    en_fs, es_fs, fixes_json, out_fs = sys.argv[1:5]
    fixes = json.load(open(fixes_json, encoding="utf-8"))
    mapping = {f["en"]: f["es"] for f in fixes if f["en"] != f["es"]}

    _, en_objs = E.parse_fs(open(en_fs, "rb").read())
    f_es, es_objs = E.parse_fs(open(es_fs, "rb").read())
    en_strs = scan_objects(en_objs)
    es_strs = scan_objects(es_objs)

    if len(en_strs) != len(es_strs):
        print("ERROR: numero de objetos distinto EN vs ES"); sys.exit(1)

    edits = {}          # objeto -> [(pos, old_len, new_bytes)]
    hit = {}            # en -> nº sustituciones
    for k in range(len(en_strs)):
        a, b = en_strs[k], es_strs[k]
        if len(a) != len(b):
            print(f"AVISO: objeto {k} con nº cadenas distinto "
                  f"({len(a)} vs {len(b)}); se omite")
            continue
        for i, it in enumerate(a):
            en = it["text"]
            if en not in mapping:
                continue
            cur = b[i]["text"]
            new = mapping[en]
            if cur == new:
                continue
            # posicion del texto en el cuerpo del objeto ES (tras 4 bytes len)
            q = b[i]["pos"] - 4
            edits.setdefault(k, []).append((q, b[i]["len"], new.encode("utf-8")))
            hit[en] = hit.get(en, 0) + 1

    applied = 0
    for k, lst in edits.items():
        body = es_objs[k]["body"]
        for q, old_len, nb in sorted(lst, key=lambda x: -x[0]):
            body[q:q + 4 + old_len] = struct.pack(">I", len(nb)) + nb
            applied += 1

    out = E.emit_fs(f_es, es_objs)
    open(out_fs, "wb").write(out)

    nohit = [en for en in mapping if en not in hit]
    print(f"fixes en el JSON      : {len(mapping)}")
    print(f"sustituciones aplicadas: {applied}")
    print(f"objetos modificados    : {len(edits)}")
    print(f"claves sin aplicar     : {len(nohit)}")
    for en in nohit[:15]:
        print("   sin aplicar:", repr(en[:60]))
    print(f"{os.path.getsize(es_fs)} -> {len(out)} bytes")
    print("->", out_fs)


if __name__ == "__main__":
    main()
