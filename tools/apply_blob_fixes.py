#!/usr/bin/env python3
"""Traduce cadenas dentro de OBJETOS COMPRIMIDOS (zlib) de un `.fs`.

Contexto (ver docs/ESTADO_TRADUCCION.md):
  El bloque de datos de un `.fs` es una secuencia de objetos. La mayoria son
  cadenas planas ``[u32 len][utf8]`` que ``simulacra_fs.scan_strings`` detecta.
  Pero algunos objetos son un ``String[]`` serializado y COMPRIMIDO con zlib
  (magic ``78 da``); su contenido NO lo ve el escaner de cadenas, por lo que
  escapa al pipeline de traduccion. Ahi viven textos de paginas web, correos y
  blog posts del juego.

Este script:
  1. Descomprime cada objeto zlib indicado.
  2. Sustituye las cadenas por coincidencia EXACTA (mismo numero y orden de
     elementos del ``String[]``).
  3. Reemite el objeto recomprimido y RECALCULA los offsets del bloque de
     formato (los objetos posteriores se desplazan al cambiar el tamano).

Entrada: JSON ``{"<indice_objeto>": {"<texto en>": "<texto es>", ...}, ...}``
  El indice de objeto es el mismo que usa ``build_locale_fs.parse_format``
  (0-based sobre ``offsets``).

Uso:
  python3 tools/apply_blob_fixes.py <in.fs> <fixes.json> <out.fs>
"""
import json
import struct
import sys
import zlib
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_locale_fs as B  # noqa: E402

_MAGICS = (b"\x78\xda", b"\x78\x9c", b"\x78\x01", b"\x78\x5e")


def is_compressed(seg):
    return seg[:2] in _MAGICS


def rewrite_payload(payload, mapping):
    """Sustituye cadenas de un String[] serializado [u32 len][utf8]."""
    out = bytearray()
    q = 0
    applied = 0
    while q + 4 <= len(payload):
        L = struct.unpack_from(">I", payload, q)[0]
        if L == 0 or L > 200000 or q + 4 + L > len(payload):
            break
        try:
            t = payload[q + 4:q + 4 + L].decode("utf-8")
        except UnicodeDecodeError:
            break
        if t in mapping:
            nb = mapping[t].encode("utf-8")
            out += struct.pack(">I", len(nb)) + nb
            applied += 1
        else:
            out += payload[q:q + 4 + L]
        q += 4 + L
    out += payload[q:]
    return bytes(out), applied


def main():
    in_fs, fixes_json, out_fs = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(in_fs, "rb").read()
    fmt, data, _ = B.split_fs(raw)
    f = B.parse_format(fmt)
    offsets = f["offsets"]
    fixes = {int(k): v for k, v in
             json.load(open(fixes_json, encoding="utf-8")).items()}

    new_data = bytearray()
    new_offsets = []
    applied_total = 0
    for k, end in enumerate(offsets):
        start = offsets[k - 1] if k > 0 else 0
        seg = data[start:end]
        if k in fixes and is_compressed(seg):
            payload = zlib.decompressobj().decompress(seg)
            new_payload, applied = rewrite_payload(payload, fixes[k])
            if applied:
                seg = zlib.compress(new_payload, 9)
                applied_total += applied
        new_data += seg
        new_offsets.append(len(new_data))

    f2 = dict(f)
    f2["offsets"] = new_offsets
    new_fmt = B.emit_format(f2)
    comp = zlib.compress(new_fmt, 9)
    out = (b"FileSystem" + B.write_int((len(comp) << 1) | 1) + comp
           + bytes(new_data))
    open(out_fs, "wb").write(out)
    print(f"objetos editados: {len(fixes)}; cadenas aplicadas: {applied_total}; "
          f"{len(raw)} -> {len(out)} bytes")


if __name__ == "__main__":
    main()
