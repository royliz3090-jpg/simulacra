#!/usr/bin/env python3
"""Verifica propuestas de correccion {objeto, indice_cadena, en, es_actual,
es_propuesto} contra el `.fs` ACTUAL, sin aplicar nada.

Para cada propuesta:
  - localiza el objeto (descomprimiendo si es zlib),
  - escanea sus cadenas (Kryo: [u32 len][utf8]),
  - toma la cadena en `indice_cadena`,
  - compara con `es_actual` (lo que la auditoria dice que hay) y con `en`
    (ingles esperado en el .fs ingles pristine).

Clasifica cada propuesta:
  APLICADA   -> el texto actual ya es `es_propuesto`
  PENDIENTE  -> el texto actual coincide con `es_actual` (o su strip) -> aplicar
  DESPLAZADA -> ni uno ni otro (indice/objeto cambiado o texto distinto)
  YA_OK      -> el texto actual no coincide con es_actual pero tampoco es
                claramente la propuesta (revisar a mano)

Uso:
  python3 tools/verify_objeto_fixes.py \
      --en work/chatgpt/en-us.fs \
      --es translations/es-LATAM/en-us.fs \
      --fixes /tmp/paquete/SIMULACRA_V2_FIXES_POR_OBJETO.json \
      --out exports/verificacion_fixes_objeto.json
"""
import argparse
import json
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402
import simulacra_fs as S  # noqa: E402


def scan_object(objs, k):
    return S.scan_strings(bytes(objs[k]["body"]))


def norm(t):
    return " ".join((t or "").split())


def classify(cur, en, es_actual, es_propuesto):
    if cur == es_propuesto:
        return "APLICADA"
    if cur == es_actual or norm(cur) == norm(es_actual):
        return "PENDIENTE"
    if norm(cur) == norm(es_propuesto):
        return "APLICADA"
    return "DESPLAZADA"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", required=True)
    ap.add_argument("--es", required=True)
    ap.add_argument("--fixes", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    _, en_objs = E.parse_fs(open(args.en, "rb").read())
    f_es, es_objs = E.parse_fs(open(args.es, "rb").read())
    fixes = json.load(open(args.fixes, encoding="utf-8"))

    en_cache, es_cache = {}, {}

    def get(objs, cache, k, idx):
        if k not in cache:
            cache[k] = scan_object(objs, k)
        lst = cache[k]
        return lst[idx]["text"] if 0 <= idx < len(lst) else None

    report = {"total": len(fixes), "APLICADA": [], "PENDIENTE": [],
              "DESPLAZADA": [], "YA_OK": []}
    for fx in fixes:
        k, idx = fx["objeto"], fx["indice_cadena"]
        cur_es = get(es_objs, es_cache, k, idx)
        cur_en = get(en_objs, en_cache, k, idx)
        if cur_es is None:
            report["DESPLAZADA"].append(
                {"fix": fx, "motivo": "indice fuera de rango",
                 "actual_es": None, "actual_en": cur_en})
            continue
        verdict = classify(cur_es, fx.get("en"), fx.get("es_actual"),
                           fx.get("es_propuesto"))
        entry = {"fix": fx, "actual_es": cur_es, "actual_en": cur_en,
                 "verdict": verdict}
        if verdict == "APLICADA":
            report["APLICADA"].append(entry)
        elif verdict == "PENDIENTE":
            report["PENDIENTE"].append(entry)
        else:
            report["DESPLAZADA"].append(entry)

    json.dump(report, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    for key in ("APLICADA", "PENDIENTE", "DESPLAZADA", "YA_OK"):
        print(f"{key:11s}: {len(report[key])}")
    print()
    for e in report["PENDIENTE"]:
        fx = e["fix"]
        print(f"  PEND obj={fx['objeto']:6d} idx={fx['indice_cadena']:2d} "
              f"cert={fx.get('certeza','?'):6s} {e['actual_es'][:40]!r} "
              f"-> {fx['es_propuesto'][:40]!r}")
    if report["DESPLAZADA"]:
        print("\n-- DESPLAZADAS (revisar) --")
        for e in report["DESPLAZADA"]:
            fx = e["fix"]
            print(f"  obj={fx['objeto']:6d} idx={fx['indice_cadena']:2d} "
                  f"actual={e['actual_es']!r} esperado={fx.get('es_actual')!r}")
    print("->", args.out)


if __name__ == "__main__":
    main()
