#!/usr/bin/env python3
"""Aplica correcciones a las cadenas de un `.fs` reconstruyendo el bloque de
objetos, de modo que las traducciones pueden tener su longitud natural.

Entrada: JSON con la lista de ediciones:
  [{"pos": <posicion del texto en el bloque de datos>, "en": "...", "es": "..."}]

`pos` es la posicion del PRIMER byte del texto (tras el prefijo de 4 bytes de
longitud), tal como la devuelve `simulacra_fs.scan_strings`. El texto actual en
esa posicion (la traduccion truncada) se sustituye por `es` completo.

Las ediciones de un mismo objeto se aplican de mayor a menor posicion para que
los desplazamientos no invaliden las posiciones anteriores.

Uso:
  python3 tools/apply_fs_fixes.py <in.fs> <fixes.json> <out.fs>
"""
import json
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402


def replace_at(body, offset, es):
    """Sustituye la cadena que empieza en `offset` (posicion del texto)."""
    p = offset - 4
    if p < 0 or p + 4 > len(body):
        return 0
    L = struct.unpack_from(">I", body, p)[0]
    if not (0 <= L <= 20000) or p + 4 + L > len(body):
        return 0
    es_b = es.encode("utf-8")
    body[p:p + 4 + L] = struct.pack(">I", len(es_b)) + es_b
    return 1


def object_of_offset(f, offset):
    for k, end in enumerate(f["offsets"]):
        if offset < end:
            return k
    return None


def main():
    in_fs, fixes_json, out_fs = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(in_fs, "rb").read()
    f, objs = E.parse_fs(raw)
    fixes = json.load(open(fixes_json, encoding="utf-8"))

    groups = {}
    for fx in fixes:
        k = object_of_offset(f, fx["pos"])
        if k is None:
            continue
        groups.setdefault(k, []).append(fx)

    applied, missing = 0, []
    for k, items in groups.items():
        if objs[k]["comp"]:
            missing += [it["en"][:60] for it in items]
            continue
        base = f["offsets"][k - 1] if k else 0
        for it in sorted(items, key=lambda x: -x["pos"]):
            if replace_at(objs[k]["body"], it["pos"] - base, it["es"]):
                applied += 1
            else:
                missing.append(it["en"][:60])

    out = E.emit_fs(f, objs)
    with open(out_fs, "wb") as fh:
        fh.write(out)
    print(f"aplicadas {applied}/{len(fixes)}; no aplicadas={len(missing)}; "
          f"{len(raw)} -> {len(out)} bytes")
    for m in missing[:20]:
        print("  FALTA:", repr(m))


if __name__ == "__main__":
    main()
