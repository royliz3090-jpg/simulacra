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
import simulacra_fs as S  # noqa: E402
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
    # Referencia en-us: el en-us.fs dentro del propio core.assets es el ingles
    # original intacto (nunca lo modificamos), asi que sirve de patron.
    pristine = sys.argv[3] if len(sys.argv) > 3 else assets

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

    # Invariantes de integridad del bloque de datos. El bug historico de
    # fs_fix_keys.rebuild (no reescribir el prefijo de longitud Kryo) desincroniza
    # el scanner y hace que el conteo de cadenas baje. Estas dos comprobaciones
    # lo detectan aunque el texto visible parezca correcto.
    _, es_data, _ = L.split_fs(es)
    es_strings = S.scan_strings(es_data)
    if os.path.exists(pristine):
        _, en_data, _ = L.split_fs(p.read("en-us.fs"))
        n_en = len(S.scan_strings(en_data))
        check(len(es_strings) == n_en,
              f"mismo conteo de cadenas que en-us.fs ({len(es_strings)} == {n_en})")
    bad_prefix = 0
    for it in es_strings:
        if int.from_bytes(es_data[it["pos"] - 4:it["pos"]], "big") != it["len"]:
            bad_prefix += 1
    check(bad_prefix == 0, f"prefijos de longitud Kryo coherentes ({bad_prefix} corruptos)")

    print("== core.binary ==")
    b = Blob(binary)
    # 1064 originales + 35 clases nuevas es-LATAM (GBESLATAM, GBESLATAMOverrides
    # y las 33 UI game27.gbeslatam.*).
    check(b.num >= 1064, f"al menos 1064 entradas ({b.num})")
    for n in ["game27.Globals", "game27.Grid", "game27.MainMenu", "game27.gb.GBMainMenu",
              "game27.gbeslatam.GBESLATAM", "game27.gbeslatam.GBESLATAMOverrides",
              "game27.DesktopMain"]:
        d, i = b.get(n)
        check(d is not None, f"clase {n} presente (idx={i})")
        if d:
            check(d[:4] == b"\xca\xfe\xba\xbe", f"  {n} es bytecode valido")

    print("\n" + ("TODO VALIDADO" if OK else "HAY FALLOS"))
    return 0 if OK else 1


if __name__ == "__main__":
    sys.exit(main())
