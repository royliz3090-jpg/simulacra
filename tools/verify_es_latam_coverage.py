#!/usr/bin/env python3
"""Verifica la cobertura de la traduccion es-LATAM de forma reproducible.

Comprueba, sin necesidad de ejecutar el juego:
  1. en-us.fs y es-latam.fs tienen el mismo numero de cadenas.
  2. No queda prosa inglesa en es-latam.fs (heuristica de palabras).
  3. Las cadenas identicas al ingles son legitimas (fechas, horas, claves,
     codigo, rutas, nombres propios) o se listan como pendientes.
  4. Los tags de interes de Spark (GlobalTexts.sparkTags) contienen todos los
     tags requeridos/opcionales de James (a3_james_tags_*), para que el
     emparejamiento del ACT3 siga funcionando.

Uso:
  python3 tools/verify_es_latam_coverage.py dist/core.assets \
      patch/game27/gbeslatam/GBESLATAM.java
"""
import re
import sys
import zipfile

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import simulacra_fs as S  # noqa: E402

EN = re.compile(
    r"\b(the|you|your|and|is|are|was|were|will|would|can|what|that|this|with|"
    r"have|has|from|they|them|their|there|here|she|her|his|but|not|for|how|"
    r"why|when|where|who|please|sorry|thank|hello|yes|about|just|like|know|"
    r"think|want|need|got|get)\b", re.I)
ES = re.compile(
    r"\b(el|la|los|las|de|que|y|es|un|una|para|con|no|se|te|tu|mi|por|como|"
    r"pero|est[aá]|est[aá]s|tienes|quiero|puedo|s[ií]|hola|gracias|porque|"
    r"cuando|d[oó]nde)\b", re.I)
DATE = re.compile(r"^\d{1,2} [A-Z][a-z]+( \d{4})?$")
DATETIME = re.compile(r"^\d{1,2} [A-Z][a-z]+ \d{4}, \d{1,2}:\d{2} [AP]M$")
TIME = re.compile(r"^\d{1,2}:\d{2}( ?[AP]M)?$")
SHORTDATE = re.compile(r"^\d{1,2} [A-Z][a-z]{2}( \d{4})?$")
COORD = re.compile(r"^[\dX ]+$")
NAME = re.compile(r"^(Greg|Taylor|Anna|Ashley|Yolanda|Cassie|Toby|Murv|"
                  r"Sara|Cody|Phill|James|Murillo|Greg Summers)$")


def strings(blob, name):
    data = blob.read(name)
    idx, off = S.split_fs(data)
    return [x["text"] for x in S.scan_strings(data[off:])]


def englishy(s):
    if len(s) < 8 or "://" in s or s.startswith(("content/", "apps/", "system/")):
        return False
    if not s.strip() or s.strip().isdigit():
        return False
    e, sp = len(EN.findall(s)), len(ES.findall(s))
    return e >= 2 and e > sp and " " in s


def legit(s):
    if (DATE.match(s) or TIME.match(s) or SHORTDATE.match(s)
            or DATETIME.match(s) or COORD.match(s) or NAME.match(s)):
        return True
    if "://" in s or s.startswith(("content/", "apps/", "system/", "web://")):
        return True
    if re.match(r"^[\w./\-]+$", s) and " " not in s:
        return True
    if re.match(r"^[A-Z_]+$", s):
        return True
    if re.search(r"[\w]+\(.*\)|[\w]+=|^!|^@", s):
        return True
    if re.match(r"^[^\w]*$", s):  # solo signos/emoticonos
        return True
    if re.match(r"^\d", s) and not re.search(r"[A-Za-z]{3}", s):
        return True
    return False


def parse_string_array(src, var):
    m = re.search(re.escape(var) + r"\s*=\s*new String\[\]\{(.*?)\}", src, re.S)
    if not m:
        return []
    return re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))


def main():
    assets = sys.argv[1] if len(sys.argv) > 1 else "dist/core.assets"
    src_path = sys.argv[2] if len(sys.argv) > 2 else \
        "patch/game27/gbeslatam/GBESLATAM.java"
    ok = True
    with zipfile.ZipFile(assets) as z:
        en, es = strings(z, "en-us.fs"), strings(z, "es-latam.fs")

    print("== conteo de cadenas ==")
    print(f"  en-us.fs  = {len(en)}")
    print(f"  es-latam  = {len(es)}")
    if len(en) != len(es):
        ok = False
        print("  FALLO: distinto numero de cadenas")
    else:
        print("  OK")

    print("== prosa inglesa en es-latam.fs ==")
    susp = sorted({es[i] for i in range(min(len(en), len(es)))
                   if englishy(es[i])})
    if susp:
        ok = False
        print(f"  FALLO: {len(susp)} candidatas")
        for s in susp[:40]:
            print("    ", repr(s))
    else:
        print("  OK: 0 candidatas")

    print("== identicas al ingles no legitimas ==")
    pend = sorted({es[i] for i in range(min(len(en), len(es)))
                   if es[i] == en[i] and not legit(es[i]) and len(es[i]) > 3})
    if pend:
        print(f"  {len(pend)} pendientes (revisar si son visibles):")
        for s in pend[:60]:
            print("    ", repr(s))
    else:
        print("  OK: 0 pendientes")

    print("== coherencia de tags de Spark (emparejamiento ACT3) ==")
    src = open(src_path, encoding="utf-8").read()
    tags = set(parse_string_array(src, "GlobalTexts.sparkTags"))
    req = set(parse_string_array(src, "GlobalTexts.a3_james_tags_required"))
    opt = set(parse_string_array(src, "GlobalTexts.a3_james_tags_optional"))
    miss = (req | opt) - tags
    print(f"  sparkTags={len(tags)} required={len(req)} optional={len(opt)}")
    if miss:
        ok = False
        print("  FALLO: tags de James ausentes en sparkTags:", sorted(miss))
    else:
        print("  OK: todos los tags de James estan en sparkTags")

    print("\n" + ("TODO VALIDADO" if ok else "HAY FALLOS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
