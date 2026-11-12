#!/usr/bin/env python3
"""Herramienta para el blob de clases de SIMULACRA (core.binary, formato KCB1).

El blob KCB1 contiene las clases Java del juego (game27.*, sengine.*, bsh.*)
empaquetadas, comprimidas con deflate y cifradas con AES/CTR/NoPadding.
La clave de cada clase es MD5(nombre_de_clase).  El vector de inicializacion
(IV) de 16 bytes precede a los datos cifrados de cada entrada.

Cabecera:
    int32  MAGIC = 1262699057 (0x4B434231 = "KCB1")
    int32  numEntries
    int32[numEntries*9] descriptor
    int32  blobSize
    byte[blobSize] blob

Cada entrada del descriptor ocupa 9 int32:
    [0..4]  hash SHA-1 del nombre (5 palabras), XOR con unlock1..5
    [5]     offset dentro del blob
    [6]     compressedSize
    [7]     uncompressedSize
    [8]     crc32 del flujo comprimido (sin cifrar)

Los campos [5..8] NO estan cifrados ni enmascarados: eso permite localizar
una entrada conocida (probando el MD5 del nombre y validando el CRC) sin
conocer la clave `unlock` derivada de la pila de ejecucion.
"""

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib

MAGIC = 1262699057


def _sha1_words(name: str):
    h = hashlib.sha1(name.encode("utf-8")).digest()
    return [
        (h[19] << 24) | (h[18] << 16) | (h[17] << 8) | h[16],
        (h[15] << 24) | (h[14] << 16) | (h[13] << 8) | h[12],
        (h[11] << 24) | (h[10] << 16) | (h[9] << 8) | h[8],
        (h[7] << 24) | (h[6] << 16) | (h[5] << 8) | h[4],
        (h[3] << 24) | (h[2] << 16) | (h[1] << 8) | h[0],
    ]


def _to_signed(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


class Blob:
    def __init__(self, path=None, data=None):
        if data is None:
            with open(path, "rb") as f:
                data = f.read()
        self.raw = data
        magic, num = struct.unpack_from(">ii", data, 0)
        if magic != MAGIC:
            raise ValueError(f"magic invalido: {magic:#x}")
        self.num = num
        off = 8
        self.desc = list(struct.unpack_from(f">{num * 9}i", data, off))
        off += num * 9 * 4
        (blob_size,) = struct.unpack_from(">i", data, off)
        off += 4
        self.blob = data[off:off + blob_size]
        if len(self.blob) != blob_size:
            raise ValueError("blob truncado")
        self.unlock = None

    def entry(self, i):
        b = i * 9
        return {
            "name_hash": self.desc[b:b + 5],
            "offset": self.desc[b + 5],
            "compressed_size": self.desc[b + 6],
            "uncompressed_size": self.desc[b + 7],
            "crc32": self.desc[b + 8] & 0xFFFFFFFF,
        }

    def _decrypt(self, name, e):
        key = hashlib.md5(name.encode("utf-8")).digest()
        from Crypto.Cipher import AES
        iv = self.blob[e["offset"]:e["offset"] + 16]
        ct = self.blob[e["offset"] + 16:e["offset"] + 16 + e["compressed_size"]]
        cipher = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv, "big"))
        comp = cipher.decrypt(ct)
        if zlib.crc32(comp) & 0xFFFFFFFF != e["crc32"]:
            return None
        return zlib.decompress(comp)

    def get(self, name):
        for i in range(self.num):
            e = self.entry(i)
            if e["compressed_size"] <= 0:
                continue
            data = self._decrypt(name, e)
            if data is not None:
                return data, i
        return None, None

    def derive_unlock(self, known_names):
        """Deriva unlock1..5 comparando el hash real con el almacenado."""
        for name in known_names:
            for i in range(self.num):
                e = self.entry(i)
                if e["compressed_size"] <= 0:
                    continue
                if self._decrypt(name, e) is None:
                    continue
                real = _sha1_words(name)
                stored = e["name_hash"]
                return [_to_signed(real[k] ^ stored[k]) for k in range(5)]
        raise RuntimeError("no se pudo derivar unlock: ninguna clase conocida coincide")

    def set_unlock(self, unlock):
        self.unlock = unlock

    def list_names(self):
        """Devuelve los nombres de las clases descifradas (requiere unlock)."""
        if self.unlock is None:
            raise RuntimeError("falta unlock")
        names = []
        for i in range(self.num):
            e = self.entry(i)
            stored = e["name_hash"]
            names.append([stored[k] ^ self.unlock[k] for k in range(5)])
        return names


def extract_all(blob_path, out_dir, roots, known_names=None):
    """Extrae clases recursivamente siguiendo referencias del constant pool."""
    import zipfile  # noqa
    blob = Blob(blob_path)
    unlock = blob.derive_unlock(known_names or ["game27.DesktopMain"])
    blob.set_unlock(unlock)
    print(f"unlock = {unlock}")

    seen = set()
    queue = list(roots)
    saved = 0
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        if not (name.startswith("game27.") or name.startswith("sengine.") or name.startswith("bsh.")):
            continue
        data, _ = blob.get(name)
        if data is None:
            continue
        saved += 1
        path = os.path.join(out_dir, name.replace(".", "/") + ".class")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        for ref in _class_refs(data):
            if ref not in seen:
                queue.append(ref)
    print(f"extraidas {saved} clases en {out_dir}")
    return unlock


def _class_refs(data):
    """Extrae nombres de clase (CONSTANT_Class) del constant pool."""
    out = set()
    try:
        import io
        f = io.BytesIO(data)
        if struct.unpack(">I", f.read(4))[0] != 0xCAFEBABE:
            return out
        f.read(4)  # minor/major
        cp = struct.unpack(">H", f.read(2))[0]
        utf = [None] * cp
        cls = [0] * cp
        i = 1
        while i < cp:
            tag = f.read(1)[0]
            if tag == 1:
                ln = struct.unpack(">H", f.read(2))[0]
                utf[i] = f.read(ln).decode("utf-8", "replace")
            elif tag == 7:
                cls[i] = struct.unpack(">H", f.read(2))[0]
            elif tag in (8, 16, 19, 20):
                f.read(2)
            elif tag == 15:
                f.read(3)
            elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
                f.read(4)
            elif tag in (5, 6):
                f.read(8)
                i += 1
            else:
                return out
            i += 1
        for i in range(1, cp):
            if cls[i] and utf[cls[i]]:
                out.add(utf[cls[i]].replace("/", "."))
    except Exception:
        pass
    return out


def repack(blob_path, classes, out_path):
    """Reconstruye un blob KCB1 a partir de un dict {nombre: bytes_de_clase}.

    Reutiliza la cabecera original (mismo numEntries) si el conjunto de
    entradas coincide; de lo contrario genera una cabecera nueva.
    """
    from Crypto.Cipher import AES
    orig = Blob(blob_path)
    unlock = orig.derive_unlock(["game27.DesktopMain"])
    names = sorted(classes.keys())
    num = len(names)
    desc = [0] * (num * 9)
    blob = bytearray()
    for i, name in enumerate(names):
        raw = classes[name]
        comp = zlib.compress(raw, 9)
        crc = zlib.crc32(comp) & 0xFFFFFFFF
        key = hashlib.md5(name.encode("utf-8")).digest()
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv, "big"))
        ct = cipher.encrypt(comp)
        offset = len(blob)
        blob += iv + ct
        h = _sha1_words(name)
        b = i * 9
        for k in range(5):
            desc[b + k] = _to_signed(h[k] ^ unlock[k])
        desc[b + 5] = offset
        desc[b + 6] = len(comp)
        desc[b + 7] = len(raw)
        desc[b + 8] = _to_signed(crc)
    with open(out_path, "wb") as f:
        f.write(struct.pack(">ii", MAGIC, num))
        f.write(struct.pack(f">{num * 9}i", *desc))
        f.write(struct.pack(">i", len(blob)))
        f.write(bytes(blob))
    return unlock


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("extract")
    p.add_argument("blob")
    p.add_argument("outdir")
    p.add_argument("--roots", default="game27.DesktopMain")
    p = sub.add_parser("info")
    p.add_argument("blob")
    p = sub.add_parser("get")
    p.add_argument("blob")
    p.add_argument("name")
    p.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "extract":
        extract_all(a.blob, a.outdir, a.roots.split(","))
    elif a.cmd == "info":
        b = Blob(a.blob)
        print(f"numEntries={b.num} blobSize={len(b.blob)}")
    elif a.cmd == "get":
        b = Blob(a.blob)
        data, i = b.get(a.name)
        if data is None:
            print("no encontrada"); sys.exit(1)
        with open(a.out, "wb") as f:
            f.write(data)
        print(f"OK entry={i} size={len(data)}")


if __name__ == "__main__":
    main()
