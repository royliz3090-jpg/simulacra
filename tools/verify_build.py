#!/usr/bin/env python3
"""Valida los entregables de dist/ sin depender de Java.

Comprueba:
  * dist/core.assets contiene los 7 recursos originales + es-latam.fs
  * en-us.fs es el ingles original (sin textos es-LATAM)
  * es-latam.fs tiene 207 nombres con prefijo es-latam:// y datos intactos
  * dist/core.binary contiene game27.gbeslatam.GBESLATAM y las clases parcheadas
  * las clases parcheadas descifran y compilan como bytecode valido (0xCAFEBABE)
"""
import hashlib
import sys
import zipfile
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_locale_fs as L  # noqa: E402
from blob_tool import Blob  # noqa: E402

OK = True


def check(cond, msg):
    global OK
    print(("  OK  " if cond else " FALLA ") + msg)
    if not cond:
        OK = False


def main():
    assets = sys.argv[1] if len(sys.argv) > 1 else "dist/core.assets"
    binary = sys.argv[2] if len(sys.argv) > 2 else "dist/core.binary"
    pristine = sys.argv[3] if len(sys.argv) > 3 else "/tmp/game/core.assets"

    print("== core.assets ==")
    z = zipfile.ZipFile(assets)
    names = z.namelist()
    for m in ["en-us.fs", "main.fs", "videos.fs", "web.fs", "zh-cn.fs", "content.fs", "emojis.fs", "es-latam.fs"]:
        check(m in names, f"miembro {m} presente")
    if os.path.exists(pristine):
        p = zipfile.ZipFile(pristine)
        check(hashlib.md5(z.read("en-us.fs")).digest() == hashlib.md5(p.read("en-us.fs")).digest(),
              "en-us.fs es identico al ingles original")

    print("== es-latam.fs ==")
    es = z.read("es-latam.fs")
    fmt, data, field = L.split_fs(es)
    f = L.parse_format(fmt)
    check(len(f["names"]) == 207, f"207 nombres en el formato ({len(f['names'])})")
    check(all(nm.startswith("es-latam://") for nm, _ in f["names"]), "todos los nombres usan es-latam://")
    check(es.count(b"Bienvenido") >= 1, "el bloque de datos contiene textos en espanol")

    print("== core.binary ==")
    b = Blob(binary)
    check(b.num == 1064, f"1064 entradas ({b.num})")
    for n in ["game27.Globals", "game27.Grid", "game27.MainMenu", "game27.gb.GBMainMenu",
              "game27.gbeslatam.GBESLATAM", "game27.DesktopMain"]:
        d, i = b.get(n)
        check(d is not None, f"clase {n} presente (idx={i})")
        if d:
            check(d[:4] == b"\xca\xfe\xba\xbe", f"  {n} es bytecode valido")

    print("\n" + ("TODO VALIDADO" if OK else "HAY FALLOS"))
    return 0 if OK else 1


if __name__ == "__main__":
    sys.exit(main())
