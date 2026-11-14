#!/usr/bin/env python3
"""Exporta el texto de UI incrustado en las clases Java del juego.

El juego guarda parte del texto (menus, dialogos de sistema, notificaciones,
pantallas de apps) como constantes de cadena dentro de las clases Java, no en
los `.fs`. Estas clases viven en `core.binary` y hay que extraerlas primero
(ver `tools/blob_tool.py`).

El juego tiene la version inglesa en `game27/gb/**` y overrides en espanol en
`game27/gbeslatam/**`. Este script empareja cada clase inglesa con su override
espanol y alinea las cadenas por (metodo, ordinal), que se ha verificado que es
el mismo orden en ambas versiones.

Entrada : directorio con las clases extraidas (por defecto /tmp/pycls).
Salida  : exports/revision_chatgpt/JAVA_UI.jsonl

Uso:
  python3 tools/blob_tool.py extract dist/core.binary /tmp/pycls
  python3 tools/export_java_ui.py --classes /tmp/pycls --out exports/revision_chatgpt
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import java_strings as J

EN_ROOT = "game27/gb"
ES_ROOT = "game27/gbeslatam"


def class_paths(root):
    """{(subruta relativa a root): ruta_absoluta}."""
    out = {}
    base = os.path.join(root, EN_ROOT)
    if not os.path.isdir(base):
        return out
    for dirpath, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".class"):
                abs_p = os.path.join(dirpath, fn)
                rel = os.path.relpath(abs_p, base)
                out[rel] = abs_p
    return out


def is_ui_text(s):
    if len(s) < 2:
        return False
    if not any(c.isalpha() for c in s):
        return False
    # descartar rutas, codigo, identificadores
    if s.startswith(("L", "[", "(", "java/", "game27/", "sengine/")):
        return False
    if "://" in s or "/" in s:
        return False
    if s.endswith((".java", ".png", ".jpg", ".ogg", ".otf", ".ttf", ".glsl")):
        return False
    if s.startswith("\\u") or s.startswith("\\n"):
        return False
    return True


def align_class(en_path, es_path):
    """Devuelve lista de (metodo, ordinal, en, es) alineadas."""
    en_m = J.ldc_by_method(en_path)
    es_m = J.ldc_by_method(es_path) if es_path else {}
    rows = []
    for (name, desc), en_seq in en_m.items():
        en_txt = [s for s in en_seq if is_ui_text(s)]
        es_seq = es_m.get((name, desc))
        es_txt = [s for s in es_seq if is_ui_text(s)] if es_seq is not None else []
        for i, en in enumerate(en_txt):
            es = es_txt[i] if i < len(es_txt) else None
            rows.append((f"{name}{desc}", i, en, es))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", default="/tmp/pycls")
    ap.add_argument("--out", default="exports/revision_chatgpt")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    en_map = class_paths(args.classes)
    es_base = os.path.join(args.classes, ES_ROOT)

    out_path = os.path.join(args.out, "JAVA_UI.jsonl")
    n = 0
    stats = {"clases_en": len(en_map), "con_override_es": 0, "sin_override_es": 0}
    missing = []
    with open(out_path, "w", encoding="utf-8") as fh:
        for rel in sorted(en_map):
            es_path = os.path.join(es_base, rel)
            es_exists = os.path.isfile(es_path)
            stats["con_override_es" if es_exists else "sin_override_es"] += 1
            if not es_exists:
                missing.append(rel)
            rows = align_class(en_map[rel], es_path if es_exists else None)
            for method, ordinal, en, es in rows:
                fl = []
                if es is None:
                    fl.append("sin_override_es")
                elif es == en:
                    fl.append("sin_traducir")
                rec = {
                    "class": "game27/gb/" + rel,
                    "method": method,
                    "ordinal": ordinal,
                    "flags": fl,
                    "en": en,
                    "es": es,
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1

    print(json.dumps(stats, indent=2))
    print("cadenas UI Java:", n)
    print("clases sin override es:", missing)
    print("->", out_path)


if __name__ == "__main__":
    main()
