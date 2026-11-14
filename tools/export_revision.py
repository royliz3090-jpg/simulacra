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
_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,}")
_TERM = ".?!…\"'»”’)]"
# Cadenas que NO deben traducirse aunque sean iguales en EN y ES:
# claves internas del juego (rompen busquedas), fechas (SimpleDateFormat US),
# colores hex, handles, correos y codigos.
_HEX = re.compile(r"^[0-9a-fA-F]{6}$")
_HANDLE = re.compile(r"^[@#][\w.]+$")
_DATE = re.compile(r"^\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}(,\s*\d{1,2}:\d{2}\s*[AP]M)?$")
_TIME = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?\s*[AP]M$")
_KEYS = None  # se carga de tools/keys_protegidas.txt


def _load_keys():
    global _KEYS
    if _KEYS is not None:
        return _KEYS
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    _KEYS = set()
    for name in ("keys_protegidas.txt", "confirmados_no_traducibles.txt"):
        try:
            with open(os.path.join(here, name), encoding="utf-8") as fh:
                _KEYS |= {l.rstrip("\n") for l in fh
                          if l.strip() and not l.startswith("#")}
        except OSError:
            pass
    return _KEYS


def is_untranslatable(en):
    """True si la cadena NO debe traducirse (clave/fecha/color/handle)."""
    if en in _load_keys():
        return True
    if _HEX.match(en) or _HANDLE.match(en) or _DATE.match(en) or _TIME.match(en):
        return True
    return False


def reviewable(rec):
    if rec["category"] not in REVIEW_CATS or rec["en"].strip() == "":
        return False
    # excluir cadenas que, quitando marcadores, no tienen prosa real
    stripped = KEEP_TOKENS.sub(" ", rec["en"])
    words = _WORD.findall(stripped)
    return len(words) >= 1


def _truncated(en, es):
    """Heuristica de truncamiento: la ES parece cortada a mitad de frase."""
    e, s = en.strip(), es.strip()
    if not s:
        return False
    # EN termina en puntuacion fuerte y ES (sin relleno) no
    if e and e[-1] in ".?!…" and s[-1] not in _TERM:
        return True
    # ES termina en palabra incompleta (letra) sin puntuacion y EN tiene mas
    if s[-1].isalpha() and e and e[-1] in ".?!…":
        return True
    return False


def issues(rec):
    """Lista de problemas detectados en la pareja EN/ES."""
    out = []
    en, es = rec["en"], rec.get("es")
    if es is None:
        return ["sin_es"]
    if es == en:
        # no es un problema si la cadena es una clave/fecha/color/handle
        if not is_untranslatable(en):
            out.append("sin_traducir")
    if _truncated(en, es):
        out.append("posible_truncado")
    # marcadores presentes en EN pero ausentes en ES (o viceversa)
    me = Counter(KEEP_TOKENS.findall(en))
    ms = Counter(KEEP_TOKENS.findall(es))
    if me != ms:
        out.append("marcadores_distintos")
    # contenido probablemente perdido: muchas menos palabras en ES que en EN
    enw = len(_WORD.findall(en))
    esw = len(_WORD.findall(es))
    if enw >= 5 and esw <= 0.34 * enw:
        out.append("contenido_faltante")
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

    # --- vista deduplicada (la mas util para revisar con ChatGPT) ---
    uniq = {}
    for owner, recs in by_owner.items():
        for rec in recs:
            key = (rec["en"], rec.get("es"))
            u = uniq.setdefault(key, {"en": rec["en"], "es": rec.get("es"),
                                      "count": 0, "owners": set(),
                                      "problemas": set(), "category": rec["category"]})
            u["count"] += 1
            u["owners"].add(owner)
            u["problemas"].update(rec["problemas"])
    uniq_rows = sorted(uniq.values(), key=lambda u: (-len(u["problemas"]), -u["count"], u["en"]))

    ujsonl = os.path.join(args.out, "UNICOS.jsonl")
    with open(ujsonl, "w", encoding="utf-8") as fh:
        for u in uniq_rows:
            fh.write(json.dumps({
                "en": u["en"], "es": u["es"], "categoria": u["category"],
                "repeticiones": u["count"], "problemas": sorted(u["problemas"]),
                "recursos": sorted(u["owners"]),
            }, ensure_ascii=False) + "\n")

    umd = os.path.join(args.out, "UNICOS.md")
    with open(umd, "w", encoding="utf-8") as fh:
        fh.write("# SIMULACRA - textos UNICOS para revision (EN -> es-LATAM)\n\n")
        fh.write(f"Pares unicos: {len(uniq_rows)}  (de {total} ocurrencias)\n\n")
        fh.write("Cada entrada: `EN` original, `ES` traduccion actual, numero de veces "
                 "que aparece y problemas detectados.\n\n")
        for u in uniq_rows:
            tag = f"  [{','.join(sorted(u['problemas']))}]" if u["problemas"] else ""
            en = u["en"].replace("\n", "\\n")
            es = (u["es"] or "").replace("\n", "\\n")
            fh.write(f"- EN: {en}\n  ES: {es}  (x{u['count']}){tag}\n")

    print(f"pares unicos: {len(uniq_rows)}")
    print("->", jsonl_path)
    print("->", md)
    print("->", idx)
    print("->", ujsonl)
    print("->", umd)

    # LOTE2: solo lo que sigue marcado con problemas (para la siguiente pasada)
    flagged_rows = [u for u in uniq_rows if u["problemas"]]
    l2j = os.path.join(args.out, "LOTE2.jsonl")
    with open(l2j, "w", encoding="utf-8") as fh:
        for u in flagged_rows:
            fh.write(json.dumps({
                "en": u["en"], "es": u["es"], "categoria": u["category"],
                "repeticiones": u["count"], "problemas": sorted(u["problemas"]),
                "recursos": sorted(u["owners"]),
            }, ensure_ascii=False) + "\n")
    l2m = os.path.join(args.out, "LOTE2.md")
    with open(l2m, "w", encoding="utf-8") as fh:
        fh.write("# SIMULACRA - LOTE 2: solo cadenas con incidencias\n\n")
        fh.write(f"Pares con incidencia: {len(flagged_rows)}\n\n")
        fh.write("Traduce/corrige cada `ES` para que corresponda a su `EN`.\n\n")
        for u in flagged_rows:
            tag = ",".join(sorted(u["problemas"]))
            en = u["en"].replace("\n", "\\n")
            es = (u["es"] or "").replace("\n", "\\n")
            fh.write(f"- EN: {en}\n  ES: {es}  [{tag}]  (x{u['count']})\n")
    print(f"lote2 (con incidencias): {len(flagged_rows)}")
    print("->", l2j)
    print("->", l2m)


if __name__ == "__main__":
    main()
