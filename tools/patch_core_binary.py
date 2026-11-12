#!/usr/bin/env python3
"""Parchea core.binary (blob KCB1) reemplazando/agregando clases.

Estrategia conservadora: se conservan intactas las palabras [0..4] del
descriptor (hash del nombre ya enmascarado con `unlock`) de cada entrada
original, y solo se recalculan [5..8] (offset, tamano comprimido, tamano
sin comprimir, crc32). Asi no hace falta conocer el nombre de cada clase
para reubicarla. Las entradas nuevas si necesitan su nombre.

Uso:
    python3 tools/patch_core_binary.py core.binary salida.binary \
        --replace game27.Globals=Clases/game27/Globals.class \
        --add game27.gbeslatam.GBESLATAM=Clases/game27/gbeslatam/GBESLATAM.class
"""
import argparse
import hashlib
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blob_tool import Blob, MAGIC, _sha1_words, _to_signed  # noqa: E402


def _encrypt(name, raw):
    from Crypto.Cipher import AES
    comp = zlib.compress(raw, 9)
    crc = zlib.crc32(comp) & 0xFFFFFFFF
    key = hashlib.md5(name.encode("utf-8")).digest()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv, "big"))
    ct = cipher.encrypt(comp)
    return iv + ct, comp, crc


def patch(blob_path, out_path, replaces, adds):
    """replaces: {nombre: ruta .class}; adds: {nombre: ruta .class}"""
    orig = Blob(blob_path)
    unlock = orig.derive_unlock(["game27.DesktopMain"])
    um = [u & 0xFFFFFFFF for u in unlock]

    new_blob = bytearray()
    desc = []

    # Entradas originales, en orden. Se conserva el hash [0..4].
    for i in range(orig.num):
        e = orig.entry(i)
        name = None
        # identificar por hash para saber si hay reemplazo
        key = tuple((e["name_hash"][k] & 0xFFFFFFFF) ^ um[k] for k in range(5))
        for nm in replaces:
            if tuple(_sha1_words(nm)) == key:
                name = nm
                break
        if name is not None:
            raw = open(replaces[name], "rb").read()
            data, comp, crc = _encrypt(name, raw)
            uncompsize = len(raw)
            compsize = len(comp)
        else:
            off0 = e["offset"]
            compsize = e["compressed_size"]
            uncompsize = e["uncompressed_size"]
            crc = e["crc32"]
            data = orig.blob[off0:off0 + 16 + compsize]
        offset = len(new_blob)
        new_blob += data
        desc.append([e["name_hash"][k] for k in range(5)] + [offset, compsize, uncompsize, _to_signed(crc)])

    # Entradas nuevas.
    for name, path in adds.items():
        raw = open(path, "rb").read()
        data, comp, crc = _encrypt(name, raw)
        offset = len(new_blob)
        new_blob += data
        h = _sha1_words(name)
        hw = [_to_signed(h[k] ^ unlock[k]) for k in range(5)]
        desc.append(hw + [offset, len(comp), len(raw), _to_signed(crc)])

    num = len(desc)
    flat = [v for row in desc for v in row]
    with open(out_path, "wb") as f:
        f.write(struct.pack(">ii", MAGIC, num))
        f.write(struct.pack(f">{num * 9}i", *flat))
        f.write(struct.pack(">i", len(new_blob)))
        f.write(bytes(new_blob))
    return num


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blob")
    ap.add_argument("out")
    ap.add_argument("--replace", action="append", default=[], help="nombre=ruta.class")
    ap.add_argument("--add", action="append", default=[], help="nombre=ruta.class")
    a = ap.parse_args()
    replaces = dict(x.split("=", 1) for x in a.replace)
    adds = dict(x.split("=", 1) for x in a.add)
    num = patch(a.blob, a.out, replaces, adds)
    print(f"escrito {a.out}: {num} entradas (+{len(adds)} nuevas, {len(replaces)} reemplazadas)")


if __name__ == "__main__":
    main()
