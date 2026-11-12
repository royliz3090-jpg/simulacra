#!/usr/bin/env python3
"""Construye un `.fs` de idioma nuevo (p. ej. es-latam.fs) a partir de otro.

Idea clave (ver docs/ARQUITECTURA_IDIOMA.md):
  El juego resuelve el contenido como `Globals.contentPrefix + filename`, y
  `contentPrefix` es p. ej. "en-us://".  El bloque de DATOS de un `.fs` NO
  contiene el prefijo; el prefijo solo aparece en los NOMBRES del bloque de
  formato (el mapa nombre->id).  Por eso, para crear un idioma nuevo basta:

    1. Reutilizar el bloque de datos (texto) de un `.fs` ya traducido.
    2. Reescribir los nombres del bloque de formato cambiando el prefijo
       ("en-us://" -> "es-latam://").
    3. Reemitir cabecera + formato + datos.

Los offsets del bloque de formato apuntan al bloque de DATOS, que no cambia,
asi que no hay que recalcularlos.

Formato de un `.fs` (Mass "FileSystem"):
    "FileSystem"          (10 bytes)
    int32 field           field = size<<1 | (isCompressed ? 1 : 0)
    byte[size] format     bloque de formato (comprimido con zlib o no)
    byte[...]  data       bloque de datos (objetos serializados)

Bloque de formato descomprimido (Mass.save + MassFile.writeFormatData):
    int32 totalSerialized
    int32[total] types
    int32[total] offsets
    int32[total] mapOffsets
    int32[mapSize] map            (mapSize = mapOffsets[total-1])
    int32 serializersId
    { int32 id; string typeName; string serializerName } * serializersId
    int32 namesCount
    { string name; int32 id } * namesCount
"""
import argparse
import io
import struct
import sys
import zipfile
import zlib


def read_int(buf, pos):
    return struct.unpack_from(">i", buf, pos)[0], pos + 4


def read_string(buf, pos):
    n, pos = read_int(buf, pos)
    if n < 0:
        return None, pos
    s = buf[pos:pos + n].decode("utf-8")
    return s, pos + n


def write_int(value):
    return struct.pack(">i", value)


def write_string(value):
    if value is None:
        return write_int(-1)
    b = value.encode("utf-8")
    return write_int(len(b)) + b


def split_fs(raw):
    """Devuelve (format_block_descomprimido, data_block, field).

    Algunas variantes del juego escriben el campo de cabecera de forma que no
    coincide con el numero real de bytes del bloque de formato. Por eso se
    valida cada interpretacion y se cae al flujo zlib cuando hace falta.
    """
    if raw[:10] != b"FileSystem":
        raise ValueError("no es un .fs (falta cabecera FileSystem)")
    field = struct.unpack_from(">i", raw, 10)[0]
    size = field >> 1
    compressed = bool(field & 1)

    # Interpretacion 1: fiel a la cabecera.
    try:
        fmt_raw = raw[14:14 + size]
        if len(fmt_raw) == size:
            fmt = zlib.decompress(fmt_raw) if compressed else fmt_raw
            parse_format(fmt)  # valida que consume el bloque entero
            return fmt, raw[14 + size:], field
    except Exception:
        pass

    # Interpretacion 2: bloque de formato como flujo zlib desde el byte 14.
    dec = zlib.decompressobj()
    fmt = dec.decompress(raw[14:])
    consumed = len(raw) - 14 - len(dec.unused_data)
    parse_format(fmt)
    return fmt, raw[14 + consumed:], field


def parse_format(fmt):
    """Devuelve un dict con todas las secciones del bloque de formato."""
    p = 0
    total, p = read_int(fmt, p)
    types = list(struct.unpack_from(f">{total}i", fmt, p)); p += 4 * total
    offsets = list(struct.unpack_from(f">{total}i", fmt, p)); p += 4 * total
    map_offsets = list(struct.unpack_from(f">{total}i", fmt, p)); p += 4 * total
    map_size = map_offsets[-1] if total else 0
    mapv = list(struct.unpack_from(f">{map_size}i", fmt, p)); p += 4 * map_size
    nser, p = read_int(fmt, p)
    serializers = []
    for _ in range(nser):
        sid, p = read_int(fmt, p)
        tname, p = read_string(fmt, p)
        sname, p = read_string(fmt, p)
        serializers.append((sid, tname, sname))
    ncount, p = read_int(fmt, p)
    names = []
    for _ in range(ncount):
        nm, p = read_string(fmt, p)
        oid, p = read_int(fmt, p)
        names.append((nm, oid))
    if p != len(fmt):
        raise ValueError(f"bloque de formato con {len(fmt) - p} bytes sobrantes")
    return {
        "total": total, "types": types, "offsets": offsets,
        "map_offsets": map_offsets, "map": mapv, "serializers": serializers,
        "names": names,
    }


def emit_format(f):
    out = io.BytesIO()
    out.write(write_int(f["total"]))
    out.write(struct.pack(f">{f['total']}i", *f["types"]))
    out.write(struct.pack(f">{f['total']}i", *f["offsets"]))
    out.write(struct.pack(f">{f['total']}i", *f["map_offsets"]))
    out.write(struct.pack(f">{len(f['map'])}i", *f["map"]))
    out.write(write_int(len(f["serializers"])))
    for sid, tname, sname in f["serializers"]:
        out.write(write_int(sid))
        out.write(write_string(tname))
        out.write(write_string(sname))
    out.write(write_int(len(f["names"])))
    for nm, oid in f["names"]:
        out.write(write_string(nm))
        out.write(write_int(oid))
    return out.getvalue()


def rewrite_prefix(names, old_prefix, new_prefix):
    out = []
    changed = 0
    for nm, oid in names:
        if nm is not None and nm.startswith(old_prefix):
            nm = new_prefix + nm[len(old_prefix):]
            changed += 1
        out.append((nm, oid))
    return out, changed


def build_fs(source_fs_bytes, old_prefix, new_prefix, compress=True):
    fmt, data, _ = split_fs(source_fs_bytes)
    f = parse_format(fmt)
    f["names"], changed = rewrite_prefix(f["names"], old_prefix, new_prefix)
    new_fmt = emit_format(f)
    if compress:
        comp = zlib.compress(new_fmt, 9)
        field = (len(comp) << 1) | 1
        fmt_out = comp
    else:
        field = len(new_fmt) << 1
        fmt_out = new_fmt
    out = b"FileSystem" + write_int(field) + fmt_out + data
    return out, changed, len(f["names"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assets", help="core.assets de origen")
    ap.add_argument("member", help="miembro .fs de origen (p. ej. en-us.fs)")
    ap.add_argument("out", help="archivo .fs de salida")
    ap.add_argument("--old-prefix", default="en-us://")
    ap.add_argument("--new-prefix", default="es-latam://")
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--direct", action="store_true",
                    help="tratar `assets` como un .fs crudo (no como ZIP)")
    a = ap.parse_args()
    if a.direct:
        src = open(a.assets, "rb").read()
    else:
        with zipfile.ZipFile(a.assets) as z:
            src = z.read(a.member)
    out, changed, total = build_fs(src, a.old_prefix, a.new_prefix,
                                   compress=not a.no_compress)
    with open(a.out, "wb") as fh:
        fh.write(out)
    print(f"OK {a.member} -> {a.out}: {changed}/{total} nombres reescritos "
          f"({a.old_prefix} -> {a.new_prefix}), {len(out)} bytes")


if __name__ == "__main__":
    main()
