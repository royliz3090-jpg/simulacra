#!/usr/bin/env python3
"""Valida una lista de correcciones {en, es} contra la extraccion completa.

Comprueba que cada `en` existe en el recurso, que no se pierden marcadores
protegidos, que se conserva el numero de saltos de linea y que no hay claves
inventadas. Genera un informe y un subconjunto "seguro" listo para aplicar.

Uso:
  python3 tools/validate_fixes.py --fixes fixes.json \
      --jsonl exports/simulacra_textos_completos.jsonl \
      --out exports/validacion_fixes.json
"""
import argparse
import json
import re
from collections import Counter, defaultdict

# Marcadores que NUNCA deben perderse ni alterarse.
KEEP_TOKENS = re.compile(r"#[\w.:]+#|__[A-Z]+\d*|\[[A-Z_]+\]|\[\]|\{\w+\}")
URI_PREFIX = re.compile(r"\b(?:corrupted|photoroll|vo|graphic|web|audio|videos)://")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixes", default="fixes.json")
    ap.add_argument("--jsonl", default="exports/simulacra_textos_completos.jsonl")
    ap.add_argument("--out", default="exports/validacion_fixes.json")
    args = ap.parse_args()

    fixes = json.load(open(args.fixes, encoding="utf-8"))
    fixes = [f for f in fixes if f.get("en") != f.get("es")]

    # ocurrencias de cada EN en la extraccion
    occ = defaultdict(list)
    for line in open(args.jsonl, encoding="utf-8"):
        r = json.loads(line)
        occ[r["en"]].append(r)

    report = {"total_fixes": len(fixes), "ok": [], "avisos": [], "errores": []}
    seen = set()
    for f in fixes:
        en, es = f["en"], f["es"]
        probs = []
        if en in seen:
            probs.append("en_duplicado_en_fixes")
        seen.add(en)
        if en not in occ:
            probs.append("en_no_encontrado")
        # marcadores
        if Counter(KEEP_TOKENS.findall(en)) != Counter(KEEP_TOKENS.findall(es)):
            probs.append("marcadores_distintos")
        # uris
        if Counter(URI_PREFIX.findall(en)) != Counter(URI_PREFIX.findall(es)):
            probs.append("uris_distintas")
        # saltos de linea
        if en.count("\n") != es.count("\n"):
            probs.append(f"newlines_{en.count(chr(10))}_vs_{es.count(chr(10))}")
        # sin cambios efectivos (solo espacios)
        if en.strip() == es.strip():
            probs.append("sin_cambio_real")
        entry = {
            "en": en, "es": es,
            "ocurrencias": len(occ.get(en, [])),
            "recursos": sorted({o["owner"] for o in occ.get(en, [])}),
            "problemas": probs,
        }
        if "en_no_encontrado" in probs or "sin_cambio_real" in probs:
            report["errores"].append(entry)
        elif probs:
            report["avisos"].append(entry)
        else:
            report["ok"].append(entry)

    json.dump(report, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"fixes totales      : {report['total_fixes']}")
    print(f"  OK (aplicables)  : {len(report['ok'])}")
    print(f"  avisos           : {len(report['avisos'])}")
    print(f"  errores          : {len(report['errores'])}")
    print(f"apariciones cubiertas: {sum(e['ocurrencias'] for e in report['ok'])}")
    if report["errores"]:
        print("\n-- errores --")
        for e in report["errores"][:20]:
            print("   ", e["problemas"], repr(e["en"][:60]))
    print("\n-- avisos (muestra) --")
    for e in report["avisos"][:20]:
        print("   ", e["problemas"], repr(e["en"][:50]), "->", repr(e["es"][:50]))
    print("->", args.out)


if __name__ == "__main__":
    main()
