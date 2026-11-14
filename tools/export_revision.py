#!/usr/bin/env python3
"""Genera el paquete de revision para ChatGPT a partir de la auditoria completa.

Entrada : exports/simulacra_textos_completos.jsonl  (lo produce export_auditoria.py)
Salidas :
  exports/revision_chatgpt/REVISION.jsonl    solo textos narrativos y de UI,
                                             con EN y ES, marcados por problema.
  exports/revision_chatgpt/REVISION.md       version legible agrupada por recurso.
  exports/revision_chatgpt/INDICE_RECURSOS.md inventario de recursos y conteos.

Uso:
  python3 tools/export_revision.py [--src exports/simulacra_textos_completos.jsonl]
                                   [--out exports/revision_chatgpt]
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

REVIEW_CATS = {"narrativo", "ui"}
# Marcadores que NUNCA deben traducirse ni perderse.
KEEP_TOKENS = re.compile(r"#[\w.:]+#|__[A-Z]+\d*|\[[A-Z_]+\]|\[\]|\{\w+\}")


def reviewable(rec):
    return rec["category"] in REVIEW_CATS and rec["en"].strip() != ""


def issues(rec):
    """Lista de problemas detectados en la pareja EN/ES."""
    out = []
    en, es = rec["en"], rec.get("es")
    if es is None:
        return ["sin_es"]
    if es == en:
        out.append("sin_traducir")
    if es != es.rstrip() and es.strip():
        out.append("relleno_espacios")
    # marcadores presentes en EN pero ausentes en ES (o viceversa)
    me = Counter(KEEP_TOKENS.findall(en))
    ms = Counter(KEEP_TOKENS.findall(es))
    if me != ms:
        out.append("marcadores_distintos")
    # longitud muy dispar (posible recorte)
    if en.strip() and len(es.strip()) < 0.5 * len(en.strip()) and len(en.strip()) >= 12:
        out.append("posible_recorte")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="exports/simulacra_textos_completos.jsonl")
    ap.add_argument("--out", default="exports/revision_chatgpt")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    by_owner = defaultdict(list)
    total = 0
    flagged = Counter()
    for line in open(args.src, encoding="utf-8"):
        rec = json.loads(line)
        if not reviewable(rec):
            continue
        iss = issues(rec)
        rec["problemas"] = iss
        for p in iss:
            flagged[p] += 1
        by_owner[rec["owner"]].append(rec)
        total += 1

    # REVISION.jsonl
    jsonl_path = os.path.join(args.out, "REVISION.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as fh:
        for owner in sorted(by_owner):
            for rec in by_owner[owner]:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # REVISION.md (agrupado por recurso)
    md = os.path.join(args.out, "REVISION.md")
    with open(md, "w", encoding="utf-8") as fh:
        fh.write("# SIMULACRA - textos para revision (EN -> es-LATAM)\n\n")
        fh.write(f"Total cadenas revisables: {total}\n\n")
        fh.write("Convenciones: cada linea muestra `EN` y su traduccion `ES` actual. "
                 "`[PROBLEMA]` lista incidencias detectadas automaticamente "
                 "(sin_traducir, relleno_espacios, marcadores_distintos, posible_recorte).\n\n")
        for owner in sorted(by_owner, key=lambda o: (-len(by_owner[o]), o)):
            recs = by_owner[owner]
            fh.write(f"\n## {owner}  ({len(recs)} cadenas)\n\n")
            for rec in recs:
                tag = f"  [{','.join(rec['problemas'])}]" if rec["problemas"] else ""
                en = rec["en"].replace("\n", "\\n")
                es = (rec.get("es") or "").replace("\n", "\\n")
                fh.write(f"- EN: {en}\n  ES: {es}{tag}\n")

    # INDICE_RECURSOS.md
    idx = os.path.join(args.out, "INDICE_RECURSOS.md")
    with open(idx, "w", encoding="utf-8") as fh:
        fh.write("# Indice de recursos con texto revisable\n\n")
        fh.write(f"Recursos: {len(by_owner)}   Cadenas: {total}\n\n")
        fh.write("| recurso | cadenas |\n|---|---|\n")
        for owner in sorted(by_owner, key=lambda o: -len(by_owner[o])):
            fh.write(f"| {owner} | {len(by_owner[owner])} |\n")

    print(f"revisables: {total}  recursos: {len(by_owner)}")
    print("incidencias:", dict(flagged))
    print("->", jsonl_path)
    print("->", md)
    print("->", idx)


if __name__ == "__main__":
    main()
