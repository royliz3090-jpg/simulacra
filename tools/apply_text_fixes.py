#!/usr/bin/env python3
"""Aplica correcciones de traduccion por COINCIDENCIA DE TEXTO en un `.fs`.

A diferencia de ``apply_fs_fixes.py`` (que usa posiciones absolutas, fragiles
cuando el prefijo de los URI cambia entre ``en-us://`` y ``es-latam://``), esta
herramienta localiza la cadena por su contenido y la sustituye, preservando el
resto de la estructura. Recorre SOLO las cadenas planas del bloque de datos
(las de objetos comprimidos se corrigen con ``apply_blob_fixes.py``).

Entrada: JSON lista de ediciones ``[{"en": "<texto actual>", "es": "<nuevo>"}]``.

Uso:
  python3 tools/apply_text_fixes.py <in.fs> <fixes.json> <out.fs>
"""
import json
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402


def main():
    in_fs, fixes_json, out_fs = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(in_fs, "rb").read()
    f, objs = E.parse_fs(raw)
    fixes = json.load(open(fixes_json, encoding="utf-8"))
    mapping = {fx["en"]: fx["es"] for fx in fixes if fx["en"] != fx["es"]}

    applied, seen = 0, set()
    for k, ob in enumerate(objs):
        if ob["comp"]:
            continue
        body = ob["body"]
        q, n = 0, len(body)
        while q + 4 <= n:
            L = struct.unpack_from(">I", body, q)[0]
            if L == 0 or L > 200000 or q + 4 + L > n:
                break
            try:
                t = body[q + 4:q + 4 + L].decode("utf-8")
            except UnicodeDecodeError:
                break
            if t in mapping:
                nb = mapping[t].encode("utf-8")
                body[q:q + 4 + L] = struct.pack(">I", len(nb)) + nb
                applied += 1
                seen.add(t)
                q += 4 + len(nb)
                continue
            q += 4 + L

    out = E.emit_fs(f, objs)
    with open(out_fs, "wb") as fh:
        fh.write(out)
    miss = set(mapping) - seen
    print(f"aplicadas {applied} sustituciones; "
          f"{len(raw)} -> {len(out)} bytes")
    for m in sorted(miss):
        print("  NO ENCONTRADA:", repr(m[:60]))


if __name__ == "__main__":
    main()
