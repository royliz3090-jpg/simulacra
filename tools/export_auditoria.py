#!/usr/bin/env python3
"""Exporta el 100% de los textos de SIMULACRA para auditoria/traduccion.

Lee `core.assets` (ZIP) y extrae TODAS las cadenas de `en-us.fs` (original) y
`es-latam.fs` (traduccion actual), alineadas por objeto y por ordinal. Para cada
cadena anota:

  - owner:  recurso raiz que la contiene (content/chats/greg, content/mail/...),
            resuelto siguiendo el grafo de referencias `map` (ver
            docs/AUDITORIA_ARQUITECTURA.md).
  - type:   clase del serializador del objeto que la contiene.
  - ordinal: posicion de la cadena dentro del objeto (0, 1, 2, ...).
  - category: narrativo / ui / tecnico / marcador.
  - flags:  untranslated (ES == EN), padded (espacios finales de relleno),
            truncated (posible recorte), has_marker (contiene #var#, []...).

Salida (una linea JSON por ocurrencia, sin duplicar por (owner,obj,ordinal)):
  exports/simulacra_textos_completos.jsonl
  exports/simulacra_resumen.json

Uso:
  python3 tools/export_auditoria.py [--assets dist/core.assets] [--out exports]
"""
import argparse
import json
import os
import re
import sys
import zipfile
import zlib
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_locale_fs as B
import simulacra_fs as S


# ---------------------------------------------------------------------------
# Carga de un miembro .fs
# ---------------------------------------------------------------------------
def load_fs(raw):
    """Devuelve (fmt_dict, objs) con objs = [(comprimido, bytes_crudos)]."""
    fmt, data, _ = B.split_fs(raw)
    f = B.parse_format(fmt)
    objs = []
    prev = 0
    for k in range(f["total"]):
        chunk = data[prev:f["offsets"][k]]
        isc = bool(f["types"][k] & 1)
        body = zlib.decompress(chunk) if isc else chunk
        objs.append((isc, body))
        prev = f["offsets"][k]
    return f, objs


def build_adjacency(f):
    """Grafo de referencias: adj[k] = lista de indices de objeto referenciados."""
    mo, mp = f["map_offsets"], f["map"]
    total = f["total"]
    adj = []
    for k in range(total):
        a = mo[k - 1] if k > 0 else 0
        b = mo[k]
        adj.append([v >> 2 for v in mp[a:b] if (v & 3) == 3])
    return adj


def compute_owners(f, adj):
    """owner_primary[obj] = recurso raiz; owner_all[obj] = lista de recursos."""
    names = f["names"]  # [(uri, oid), ...]
    total = f["total"]
    owner_all = defaultdict(list)
    owner_primary = [None] * total
    # ordenar por nombre para que el "primario" sea determinista
    for uri, oid in sorted(names, key=lambda x: x[0]):
        short = uri.split("://", 1)[1] if "://" in uri else uri
        seen = {oid}
        stack = [oid]
        while stack:
            k = stack.pop()
            owner_all[k].append(short)
            if owner_primary[k] is None:
                owner_primary[k] = short
            for r in adj[k]:
                if r not in seen and 0 <= r < total:
                    seen.add(r)
                    stack.append(r)
    return owner_primary, owner_all


# ---------------------------------------------------------------------------
# Clasificacion de cadenas
# ---------------------------------------------------------------------------
_TECH_PREFIX = ("content/", "graphic://", "apps/", "system/", "shaders/",
                "corrupted://", "web://", "audio/", "videos/")
_TECH_EXT = (".png", ".jpg", ".jpeg", ".ogg", ".wav", ".mp3", ".glsl", ".json",
             ".web", ".otf", ".ttf", ".mp4", ".atlas", ".fnt", ".gif", ".svg")
_DATE_RE = re.compile(r"^\d{1,2}\s+[A-Za-z]{3,}(\s+\d{4})?$")
_TIME_RE = re.compile(r"^\d{1,2}:\d{2}\s*(AM|PM)?$", re.I)
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_./$@:\-]*$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+$")
_MARKER_RE = re.compile(r"#\w+[.:]?|__[A-Z]+\d*|\[\w+\]|\[\]|\{\w+\}")
# GLSL / shader
_GLSL_RE = re.compile(r"gl_|vec[234]|uniform\s|varying|precision\s|attribute\s|#ifdef|void\s+main")
# codigo/trigger: foo.bar(), nombre.Clase.metodo()
_CODE_RE = re.compile(r"^[A-Za-z_][\w.$]*(\.[A-Za-z_]\w*)+\(.*\)$")
# llamada a funcion/trigger en cualquier linea (multilinea incluida)
_CODE_CALL_RE = re.compile(r"^\s*[A-Za-z_][\w.$]*\s*\(", re.S)
_CODE_MARK_RE = re.compile(r"\(\)\s*;|\bTriggers\.|\bGlobals\.|Achievement\.|\bsave[A-Z]\w*\(|\bquest[A-Z]\w*\(")
# etiqueta de condicion/estado: "!algo_sin_espacios"
_TAG_RE = re.compile(r"^![\w.]*$")
# etiqueta UI de una sola palabra capitalizada: "Camera", "Gallery", "Okay."
_LABEL_RE = re.compile(r"^[A-Z][a-z]+\.?$")


def is_tech(s):
    if s.startswith(_TECH_PREFIX):
        # prefijo tecnico, pero si tras un salto de linea hay prosa, es narrativo
        if "\n" in s:
            body = s.split("\n", 1)[1]
            if len(re.findall(r"[A-Za-z]{2,}", body)) >= 3:
                return False
        return True
    if _TAG_RE.match(s):
        return True
    if _CODE_MARK_RE.search(s) and _CODE_CALL_RE.match(s):
        return True
    if "://" in s and "\n" not in s:
        return True
    if _GLSL_RE.search(s):
        return True
    if _CODE_RE.match(s):
        return True
    low = s.lower()
    if low.endswith(_TECH_EXT):
        return True
    if _DATE_RE.match(s) or _TIME_RE.match(s) or _EMAIL_RE.match(s):
        return True
    if " " not in s:
        # una sola palabra: etiqueta UI si es Capitalizada simple; si no, identificador
        if _LABEL_RE.match(s):
            return False
        if _IDENT_RE.match(s):
            return True
    return False


def classify(s):
    if not s:
        return "vacio"
    if is_tech(s):
        return "tecnico"
    if _MARKER_RE.search(s):
        # contiene marcadores -> narrativo si ademas tiene prosa
        if " " in s and sum(c.isalpha() for c in s) >= 2:
            return "narrativo"
        return "marcador"
    letters = sum(c.isalpha() for c in s)
    words = s.split()
    if letters >= 2 and (len(words) >= 3 or (len(words) >= 1 and len(s) >= 20)):
        return "narrativo"
    if letters >= 1:
        return "ui"
    return "tecnico"


def flags_for(en, es):
    fl = []
    if en == es:
        fl.append("untranslated")
    if es != es.rstrip() and es.strip():
        fl.append("padded")
    if _MARKER_RE.search(en) or _MARKER_RE.search(es):
        fl.append("has_marker")
    return fl


# tipos cuyas cadenas tienen estructura conocida [texto, remitente, fecha, hora]
_CONTACT_TYPE = "game27.model.ChatAppModel$ContactModel"
_CONTACT_ROLES = {0: "text", 1: "sender", 2: "date", 3: "time"}


def role_for(typ, idx):
    """Rol de la cadena dentro del objeto, segun estructura conocida."""
    if typ == _CONTACT_TYPE:
        return _CONTACT_ROLES.get(idx)
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="dist/core.assets")
    ap.add_argument("--out", default="exports")
    ap.add_argument("--en", default="en-us.fs")
    ap.add_argument("--es", default="es-latam.fs")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    z = zipfile.ZipFile(args.assets)
    print(f"[1/5] cargando {args.en} ...", flush=True)
    en_f, en_o = load_fs(z.read(args.en))
    print(f"      objetos EN = {len(en_o)}", flush=True)
    print(f"[2/5] cargando {args.es} ...", flush=True)
    es_f, es_o = load_fs(z.read(args.es))
    print(f"      objetos ES = {len(es_o)}", flush=True)

    ser = {sid: tn for sid, tn, sn in en_f["serializers"]}

    print("[3/5] resolviendo propietarios (grafo map) ...", flush=True)
    adj = build_adjacency(en_f)
    owner_primary, owner_all = compute_owners(en_f, adj)

    print("[4/5] extrayendo cadenas y escribiendo JSONL ...", flush=True)
    out_path = os.path.join(args.out, "simulacra_textos_completos.jsonl")
    counts = Counter()
    per_owner = Counter()
    n_rec = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for k in range(en_f["total"]):
            en_strs = S.scan_strings(bytes(en_o[k][1]))
            es_strs = S.scan_strings(bytes(es_o[k][1])) if k < len(es_o) else []
            if not en_strs:
                continue
            typ = ser.get(en_f["types"][k])
            owner = owner_primary[k] or "?"
            owners = sorted(set(owner_all.get(k, [])))
            for i, s in enumerate(en_strs):
                en = s["text"]
                es = es_strs[i]["text"] if i < len(es_strs) else None
                cat = classify(en)
                fl = flags_for(en, es) if es is not None else ["no_es"]
                rec = {
                    "owner": owner,
                    "obj": k,
                    "type": typ,
                    "ordinal": i,
                    "category": cat,
                    "flags": fl,
                    "en": en,
                    "es": es,
                }
                role = role_for(typ, i)
                if role:
                    rec["role"] = role
                if len(owners) > 1:
                    rec["shared_with"] = owners
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_rec += 1
                counts[cat] += 1
                per_owner[owner] += 1

    print(f"      registros escritos = {n_rec}", flush=True)
    print("[5/5] resumen ...", flush=True)
    summary = {
        "assets": args.assets,
        "objetos_en": len(en_o),
        "objetos_es": len(es_o),
        "cadenas_en": n_rec,
        "por_categoria": dict(counts),
        "owners": len(per_owner),
        "top_owners": per_owner.most_common(40),
        "untranslated": sum(1 for _ in ()) if False else None,
    }
    # recomputar flags agregados en una segunda pasada ligera
    untrans = padded = marker = 0
    with open(out_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            fl = r["flags"]
            if "untranslated" in fl:
                untrans += 1
            if "padded" in fl:
                padded += 1
            if "has_marker" in fl:
                marker += 1
    summary["flags"] = {"untranslated": untrans, "padded": padded, "has_marker": marker}
    with open(os.path.join(args.out, "simulacra_resumen.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nOK -> {out_path}")


if __name__ == "__main__":
    main()
