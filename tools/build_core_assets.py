#!/usr/bin/env python3
"""Ensambla core.assets con es-latam.fs como idioma independiente.

El juego lee los miembros `.fs` de core.assets como un ZIP (entradas
almacenadas, metodo 0). Para anadir un idioma nuevo basta con agregar el
miembro `es-latam.fs` conservando el resto intacto.

Uso:
    python3 tools/build_core_assets.py <core.assets_base> <salida> \
        --add es-latam.fs=ruta/es-latam.fs \
        --replace en-us.fs=ruta/en-us-pristine.fs
"""
import argparse
import zipfile
import os


def build(base, out, adds, replaces, order=None):
    zin = zipfile.ZipFile(base, "r")
    members = [i.filename for i in zin.infolist()]
    if order:
        members = order
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as zout:
        for name in members:
            if name in replaces:
                with open(replaces[name], "rb") as f:
                    zout.writestr(zipfile.ZipInfo(name), f.read())
            else:
                zout.writestr(zipfile.ZipInfo(name), zin.read(name))
        for name, path in adds.items():
            with open(path, "rb") as f:
                zout.writestr(zipfile.ZipInfo(name), f.read())
    zin.close()
    return members


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--add", action="append", default=[], help="nombre=ruta")
    ap.add_argument("--replace", action="append", default=[], help="nombre=ruta")
    a = ap.parse_args()
    adds = dict(x.split("=", 1) for x in a.add)
    replaces = dict(x.split("=", 1) for x in a.replace)
    members = build(a.base, a.out, adds, replaces)
    print(f"escrito {a.out}: {len(members)} originales + {len(adds)} nuevos "
          f"({os.path.getsize(a.out)} bytes)")


if __name__ == "__main__":
    main()
