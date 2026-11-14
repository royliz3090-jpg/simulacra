#!/usr/bin/env python3
"""Aplica correcciones identificadas por (objeto, indice_cadena) a un `.fs`.

A diferencia de `apply_fs_fixes.py` (que localiza por posicion en el bloque de
datos y NO soporta objetos comprimidos), este script trabaja con el editor
`fs_editor`, que descomprime cada objeto antes de tocar sus cadenas y vuelve a
comprimir al emitir. Por eso sirve tanto para objetos planos como zlib.

Entrada: JSON con lista de:
    {"objeto": <int>, "indice_cadena": <int>, "es_propuesto": "...",
     "en": "...", "es_actual": "..."}

Comprobaciones de seguridad por edicion:
  - el indice debe existir;
  - si `es_actual` esta presente, el texto actual debe coincidir (normalizado
    en espacios) o ser ya el `es_propuesto` (idempotencia);
  - el numero de cadenas del objeto NO cambia (nunca se anaden/quitan).

Uso:
  python3 tools/apply_index_fixes.py <in.fs> <fixes.json> <out.fs> [--report r.json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs_editor as E  # noqa: E402
import simulacra_fs as S  # noqa: E402


def norm(t):
    return " ".join((t or "").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_fs")
    ap.add_argument("fixes")
    ap.add_argument("out_fs")
    ap.add_argument("--report")
    args = ap.parse_args()

    raw = open(args.in_fs, "rb").read()
    f, objs = E.parse_fs(raw)
    fixes = json.load(open(args.fixes, encoding="utf-8"))

    # cache de cadenas por objeto
    cache = {}
    n_str = {}

    def strings(k):
        if k not in cache:
            cache[k] = S.scan_strings(bytes(objs[k]["body"]))
            n_str[k] = len(cache[k])
        return cache[k]

    applied, skipped, errors = [], [], []
    per_obj = {}
    for fx in fixes:
        k, idx = fx["objeto"], fx["indice_cadena"]
        if k >= len(objs):
            errors.append({**fx, "motivo": "objeto fuera de rango"})
            continue
        per_obj.setdefault(k, []).append(fx)

    for k, items in per_obj.items():
        # aplicar de mayor a menor posicion para no invalidar offsets
        lst = strings(k)
        edits = []
        for fx in items:
            idx = fx["indice_cadena"]
            if not (0 <= idx < len(lst)):
                errors.append({**fx, "motivo": "indice fuera de rango"})
                continue
            cur = lst[idx]["text"]
            want = fx["es_propuesto"]
            if cur == want:
                skipped.append({**fx, "motivo": "ya aplicado"})
                continue
            if "es_actual" in fx and norm(cur) != norm(fx["es_actual"]):
                errors.append({**fx, "motivo": "texto actual distinto",
                               "actual": cur})
                continue
            edits.append((lst[idx]["pos"], want, fx))
        for pos, want, fx in sorted(edits, key=lambda x: -x[0]):
            body = objs[k]["body"]
            p = pos - 4
            L = int.from_bytes(body[p:p + 4], "big")
            wb = want.encode("utf-8")
            body[p:p + 4 + L] = len(wb).to_bytes(4, "big") + wb
            applied.append(fx)
        # verificar que el numero de cadenas no cambio
        new_n = len(S.scan_strings(bytes(objs[k]["body"])))
        if new_n != len(lst):
            errors.append({"objeto": k,
                           "motivo": f"cambio de n cadenas {len(lst)}->{new_n}"})

    out = E.emit_fs(f, objs)
    open(args.out_fs, "wb").write(out)

    print(f"aplicadas : {len(applied)}")
    print(f"omitidas  : {len(skipped)} (ya aplicadas)")
    print(f"errores   : {len(errors)}")
    print(f"{len(raw)} -> {len(out)} bytes")
    for e in errors[:30]:
        print("  ERROR:", e.get("objeto"), e.get("indice_cadena"),
              e.get("motivo"), repr(e.get("actual", ""))[:40])

    if args.report:
        json.dump({"aplicadas": len(applied), "omitidas": len(skipped),
                   "errores": errors}, open(args.report, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    if errors:
        sys.exit(2)


if __name__ == "__main__":
    main()
