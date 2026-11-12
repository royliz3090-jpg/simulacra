#!/usr/bin/env python3
"""
Herramienta canónica para leer/modificar los recursos de texto de SIMULACRA.

Formato .fs (LibGDX FileSystem) usado por el juego:
  [0:14]   cabecera: b"FileSystem" + 4 bytes  (p.ej. \x00\x05=\x1f)
  [14:X]   bloque de indice comprimido con zlib  -> descomprime a un indice binario
  [X:end]  bloque de datos SIN comprimir -> objetos serializados (Kryo) con las cadenas

Estructura del indice descomprimido:
  ...
  <URI>\x00\x00 <2 bytes> <4 bytes LE>   (repetido para cada recurso; 207 URIs en en-us.fs)
  ...

Las cadenas de texto (Kryo) se almacenan como:
  <4 bytes big-endian: longitud L> <L bytes UTF-8>

Uso:
  python3 tools/simulacra_fs.py info   <core.assets>
  python3 tools/simulacra_fs.py dump   <core.assets> <en-us|zh-cn|main|web|content|videos|emojis> <salida.json>
  python3 tools/simulacra_fs.py apply  <core.assets.entrada> <traducciones.json> <core.assets.salida>
  python3 tools/simulacra_fs.py verify <core.assets> [original.assets]
"""
import sys, os, io, json, zlib, zipfile, struct, hashlib

HEADER_LEN = 14
FS_MEMBERS = ("en-us.fs", "main.fs", "videos.fs", "web.fs", "zh-cn.fs", "content.fs", "emojis.fs")


def read_zip_member(assets_path, member):
    with zipfile.ZipFile(assets_path) as z:
        return z.read(member)


def split_fs(fs_bytes):
    """Devuelve (indice_descomprimido, offset_donde_empiezan_los_datos)."""
    d = fs_bytes
    dec = zlib.decompressobj()
    index = dec.decompress(d[HEADER_LEN:])
    consumed = len(d) - HEADER_LEN - len(dec.unused_data)
    return index, HEADER_LEN + consumed


def parse_uris(index):
    """Extrae las entradas del indice: (uri, meta2, off4, posicion)."""
    out = []
    i = 0
    n = len(index)
    while True:
        p = index.find(b"://", i)
        if p < 0:
            break
        start = p
        while start > 0 and 0x21 <= index[start - 1] <= 0x7e:
            start -= 1
        end = index.find(b"\x00", p)
        uri = index[start:end]
        q = end
        while q < n and index[q] == 0:
            q += 1
        if q + 6 <= n:
            meta2, off4 = struct.unpack_from("<HI", index, q)
            out.append((uri.decode("ascii", "replace"), meta2, off4, start))
        i = end + 1
    return out


def scan_strings(data, minlen=1, maxlen=20000):
    """
    Escanea el bloque de datos buscando cadenas Kryo: 4 bytes BE de longitud + UTF-8.
    Devuelve lista de dicts {pos, len, text}.
    """
    res = []
    n = len(data)
    i = 0
    while i + 4 <= n:
        L = struct.unpack_from(">I", data, i)[0]
        if 1 <= L <= maxlen and i + 4 + L <= n:
            chunk = data[i + 4:i + 4 + L]
            try:
                s = chunk.decode("utf-8")
                if len(s) >= minlen and all((c.isprintable() or c in "\n\t\r") for c in s):
                    res.append({"pos": i + 4, "len": L, "text": s})
                    i += 4 + L
                    continue
            except UnicodeDecodeError:
                pass
        i += 1
    return res


def load_fs(assets_path, member="en-us.fs"):
    fs = read_zip_member(assets_path, member)
    index, data_off = split_fs(fs)
    data = fs[data_off:]
    return fs, index, data, data_off


def cmd_info(assets_path):
    with zipfile.ZipFile(assets_path) as z:
        names = z.namelist()
    print(f"ZIP {assets_path}: {os.path.getsize(assets_path)} bytes, {len(names)} miembros")
    for name in names:
        fs = read_zip_member(assets_path, name)
        try:
            index, off = split_fs(fs)
            uris = parse_uris(index)
            print(f"  {name:12s} fs={len(fs):9d} index={len(index):8d} data={len(fs)-off:8d} uris={len(uris)}")
        except Exception as e:
            print(f"  {name:12s} fs={len(fs):9d} ERROR {e}")


def cmd_dump(assets_path, member, out_path):
    fs, index, data, off = load_fs(assets_path, member)
    strings = scan_strings(data)
    json.dump({"member": member, "data_off": off, "strings": strings},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{member}: {len(strings)} cadenas -> {out_path}")


def cmd_apply(in_path, trans_path, out_path):
    """Aplica traducciones en sitio preservando longitud en bytes y estructura del ZIP."""
    trans = json.load(open(trans_path, encoding="utf-8"))
    with open(in_path, "rb") as f:
        orig_zip = f.read()
    zin = zipfile.ZipFile(io.BytesIO(orig_zip))
    member = trans["member"]
    fs = zin.read(member)
    index, off = split_fs(fs)
    data = bytearray(fs[off:])
    applied = 0
    for item in trans["strings"]:
        pos = item["pos"]
        new = item["es"].encode("utf-8")
        old_len = item["len"]
        if len(new) > old_len:
            raise ValueError(f"traduccion mas larga que el original en pos {pos}: {len(new)}>{old_len}")
        new = new + b" " * (old_len - len(new))
        data[pos:pos + old_len] = new
        applied += 1
    new_fs = fs[:off] + bytes(data)
    # Reconstruir ZIP preservando orden y cabeceras originales
    out = io.BytesIO()
    zout = zipfile.ZipFile(out, "w", zipfile.ZIP_STORED)
    for info in zin.infolist():
        payload = new_fs if info.filename == member else zin.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zi.internal_attr = info.internal_attr
        zi.create_system = info.create_system
        zout.writestr(zi, payload)
    zout.close()
    with open(out_path, "wb") as f:
        f.write(out.getvalue())
    print(f"aplicadas {applied} cadenas -> {out_path} ({os.path.getsize(out_path)} bytes)")
    return applied


def cmd_verify(assets_path, original=None):
    fs, index, data, off = load_fs(assets_path)
    strings = scan_strings(data)
    print(f"{assets_path}: fs={len(fs)} index={len(index)} data={len(data)} strings={len(strings)}")
    if original:
        ofs, oidx, odata, ooff = load_fs(original)
        print(f"  original: index igual={oidx==index} data_off={ooff} (actual {off})")
        os_ = {s['pos']: s for s in scan_strings(odata)}
        ns_ = {s['pos']: s for s in strings}
        changed = sum(1 for p in ns_ if p in os_ and os_[p]['text'] != ns_[p]['text'])
        same = sum(1 for p in ns_ if p in os_ and os_[p]['text'] == ns_[p]['text'])
        novel = set()
        for p in ns_:
            if p in os_ and os_[p]['text'] != ns_[p]['text']:
                novel |= (set(ns_[p]['text']) - set(os_[p]['text']))
        print(f"  cambiadas={changed} identicas={same} posiciones_nuevas={len(set(ns_)-set(os_))} posiciones_perdidas={len(set(os_)-set(ns_))}")
        print(f"  caracteres nuevos introducidos: {''.join(sorted(novel))!r}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "info":
        cmd_info(sys.argv[2])
    elif cmd == "dump":
        cmd_dump(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "apply":
        cmd_apply(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "verify":
        cmd_verify(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
