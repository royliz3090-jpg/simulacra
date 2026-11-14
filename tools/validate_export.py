#!/usr/bin/env python3
"""Valida la cobertura del export de auditoria frente al recurso real.

Comprueba que:
  1. el JSONL tiene exactamente una linea por cadena de `en-us.fs`;
  2. no falta ninguna cadena (comparacion multiset contra el `.fs`);
  3. la alineacion EN/ES por objeto cuadra (mismo numero de cadenas por objeto);
  4. resume incidencias (sin_traducir, relleno_espacios, marcadores_distintos...).

Uso:
  python3 tools/validate_export.py --assets dist/core.assets \
      --jsonl exports/simulacra_textos_completos.jsonl
"""
import argparse
import json
import sys
import zipfile
import zlib
from collections import Counter

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import build_locale_fs as B
import simulacra_fs as S


def load_fs(raw):
    fmt, data, _ = B.split_fs(raw)
    f = B.parse_format(fmt)
    objs = []
    prev = 0
    for k in range(f["total"]):
        chunk = data[prev:f["offsets"][k]]
        isc = bool(f["types"][k] & 1)
        objs.append(zlib.decompress(chunk) if isc else chunk)
        prev = f["offsets"][k]
    return f, objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="dist/core.assets")
    ap.add_argument("--jsonl", default="exports/simulacra_textos_completos.jsonl")
    args = ap.parse_args()

    z = zipfile.ZipFile(args.assets)
    en_f, en_o = load_fs(z.read("en-us.fs"))
    es_f, es_o = load_fs(z.read("es-latam.fs"))

    real = Counter()
    for body in en_o:
        for s in S.scan_strings(bytes(body)):
            real[s["text"]] += 1
    total_real = sum(real.values())

    exported = Counter()
    n_lines = 0
    flags = Counter()
    cats = Counter()
    no_es = 0
    for line in open(args.jsonl, encoding="utf-8"):
        r = json.loads(line)
        exported[r["en"]] += 1
        n_lines += 1
        for f in r["flags"]:
            flags[f] += 1
        cats[r["category"]] += 1
        if r.get("es") is None:
            no_es += 1

    ok = True
    print(f"lineas JSONL           : {n_lines}")
    print(f"cadenas en en-us.fs    : {total_real}")
    if n_lines != total_real:
        print("  !! numero de lineas != cadenas reales"); ok = False
    missing = real - exported
    extra = exported - real
    print(f"cadenas no exportadas  : {sum(missing.values())}")
    print(f"cadenas de mas         : {sum(extra.values())}")
    if missing:
        print("  !! faltan:", list(missing)[:5]); ok = False
    if extra:
        print("  !! sobran:", list(extra)[:5]); ok = False

    # alineacion por objeto
    mism = 0
    for k in range(en_f["total"]):
        if len(S.scan_strings(bytes(en_o[k]))) != len(S.scan_strings(bytes(es_o[k]))):
            mism += 1
    print(f"objetos con nº cadenas EN!=ES : {mism}")
    if mism:
        ok = False
    print(f"cadenas sin ES         : {no_es}")
    print("categorias:", dict(cats))
    print("flags:", dict(flags))
    print("\nRESULTADO:", "OK - cobertura 100%" if ok else "FALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
