#!/usr/bin/env python3
"""Editor del bloque de objetos de un `.fs` de SIMULACRA.

El bloque de datos de un `.fs` es una secuencia de objetos serializados con
Mass/Kryo. El bloque de formato guarda `offsets[k]` = posicion FINAL del
objeto k, y `types[k] & 1` indica si el objeto esta comprimido (deflate).
Esto permite reconstruir el bloque de datos con longitudes distintas sin
corromper la estructura: se sustituyen cadenas (4 bytes BE de longitud +
UTF-8) y se recalculan los offsets.

API:
    f, objs = parse_fs(bytes)      # objs = lista de dict(comp, body:bytearray)
    out     = emit_fs(f, objs)     # reemite cabecera + formato + datos

`objs[k]["body"]` es el objeto k SIN comprimir (bytes exactos del flujo Kryo).
"""
import io
import struct
import sys
import os
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_locale_fs as L  # noqa: E402


def parse_fs(raw):
    fmt, data, field = L.split_fs(raw)
    f = L.parse_format(fmt)
    offs = f["offsets"]
    types = f["types"]
    objs = []
    prev = 0
    for k in range(f["total"]):
        chunk = data[prev:offs[k]]
        comp = bool(types[k] & 1)
        body = bytearray(zlib.decompress(chunk) if comp else chunk)
        objs.append({"comp": comp, "body": body})
        prev = offs[k]
    return f, objs


def emit_fs(f, objs):
    data = bytearray()
    offs = []
    for o in objs:
        body = bytes(o["body"])
        raw = zlib.compress(body, 9) if o["comp"] else body
        data += raw
        offs.append(len(data))
    f = dict(f)
    f["offsets"] = offs
    fmt = L.emit_format(f)
    comp = zlib.compress(fmt, 9)
    field = (len(comp) << 1) | 1
    return b"FileSystem" + struct.pack(">i", field) + comp + bytes(data)


def find_strings(body):
    """Devuelve [(pos, length)] de cadenas Kryo plausibles en `body`."""
    out = []
    n = len(body)
    i = 0
    while i + 4 <= n:
        L4 = struct.unpack_from(">I", body, i)[0]
        if 1 <= L4 <= 20000 and i + 4 + L4 <= n:
            chunk = bytes(body[i + 4:i + 4 + L4])
            try:
                s = chunk.decode("utf-8")
                if all((c.isprintable() or c in "\n\t\r") for c in s):
                    out.append((i + 4, L4))
                    i += 4 + L4
                    continue
            except UnicodeDecodeError:
                pass
        i += 1
    return out


def main():
    # round-trip de prueba
    raw = open(sys.argv[1], "rb").read()
    f, objs = parse_fs(raw)
    out = emit_fs(f, objs)
    print(f"objetos={len(objs)} bytes_in={len(raw)} bytes_out={len(out)} "
          f"identico={out == raw}")


if __name__ == "__main__":
    main()
