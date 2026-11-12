#!/usr/bin/env python3
"""Genera el JSON de correcciones (formato de `apply_fs_fixes.py`) para los
subtitulos de voz (``vo://...=TEXTO``) y los mensajes de sistema de chat
(``chats://section/...``) que aun quedaban en ingles en el `.fs` es-LATAM.

La clave de traduccion es el VALOR en ingles (lo que va tras ``=`` o tras
``chats://section/``), para que cada aparicion reciba la traduccion correcta
aunque el mismo texto aparezca en varios objetos.

Uso:
  python3 tools/gen_fixes_vo_chats.py <es-latam.fs> <fixes_vo_chats.json> <out.json>
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulacra_fs as S  # noqa: E402

VO_RE = re.compile(r"^(vo://[^=]+=)(.*)$")
CHATS_RE = re.compile(r"^(chats://section/)(.*)$")


def build_edits(fs_bytes, mapping):
    idx, doff = S.split_fs(fs_bytes)
    strings = S.scan_strings(fs_bytes[doff:])
    edits = []
    seen = {}
    for s in strings:
        text = s["text"]
        m = VO_RE.match(text)
        if m:
            val = m.group(2).strip()
            if val in mapping["vo"]:
                new = m.group(1) + mapping["vo"][val]
                edits.append({"pos": s["pos"], "en": text, "es": new})
                seen[val] = seen.get(val, 0) + 1
            continue
        m = CHATS_RE.match(text)
        if m:
            val = m.group(2).strip()
            if val in mapping["chats"]:
                new = m.group(1) + mapping["chats"][val]
                edits.append({"pos": s["pos"], "en": text, "es": new})
                seen[val] = seen.get(val, 0) + 1
    return edits, seen


def main():
    fs_path, map_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mapping = json.load(open(map_path, encoding="utf-8"))
    fs = open(fs_path, "rb").read()
    edits, seen = build_edits(fs, mapping)
    json.dump(edits, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"ediciones: {len(edits)} -> {out_path}")
    missing = (set(mapping["vo"]) | set(mapping["chats"])) - set(seen)
    if missing:
        print("SIN APARICION en el .fs:")
        for m in sorted(missing):
            print("  ", repr(m))


if __name__ == "__main__":
    main()
