#!/usr/bin/env python3
"""
Genera listas de trabajo para traducir SIMULACRA:
  work/truncadas.json   - traducciones actuales truncadas (hay que reescribir mas corto)
  work/nombres.json     - nombres propios traducidos por error (dejar tal cual / corregir)
  work/pendientes.json  - cadenas que siguen en ingles
Cada entrada: {pos, len, en, es_actual}
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import simulacra_fs as S

ORIG = sys.argv[1] if len(sys.argv) > 1 else '/tmp/game/core.assets'
BASE = sys.argv[2] if len(sys.argv) > 2 else '/tmp/baseline_core.assets'
OUT = sys.argv[3] if len(sys.argv) > 3 else 'work'
os.makedirs(OUT, exist_ok=True)

o = {s['pos']: s for s in S.scan_strings(S.load_fs(ORIG, 'en-us.fs')[2])}
b = {s['pos']: s for s in S.scan_strings(S.load_fs(BASE, 'en-us.fs')[2])}

EN = set("the and you your that with have are for not but what this from will would can could should there their they them then when where which who how all any some more most other into out about over just our his her she him were was been being has had did does do say says said tell told know think going want need look like time day night phone call text message please sorry thank hello hey okay yes yeah i me my we us it is".split())

def en_words(t):
    return [w.lower() for w in re.findall(r"[A-Za-z']+", t)]

def looks_en(t):
    ws = en_words(t)
    return bool(ws) and sum(1 for w in ws if w in EN) >= 1

def is_ident(t):
    if t.startswith(('vo://', 'corrupted://', 'photoroll://', 'trigger://', 'en-us://')):
        return False
    pats = [r'^[\w./:\-]+$', r'\.(ogg|mp4|png|jpg|jpeg|web|fs|json|ttf|txt|mp3)$',
            r'^(com\.|java\.|game27\.|sengine\.|org\.)', r'://',
            r'^[A-Za-z_$][\w$]*(\.[\w$]+)+$', r'^\d+$', r'^(true|false|null|main|default|center)$',
            r'^[A-Z][A-Za-z0-9_]*(\$[A-Za-z0-9_]+)*$', r'^__[A-Z0-9_]+',
            r'^\s*$', r'^[A-Z0-9_]{2,}$', r'^(ACT\d|Triggers|Globals)', r'^state_', r'^[a-z]+\.[a-z]']
    return any(re.search(p, t) for p in pats)

def natural_end(es):
    """Heuristica: la traduccion no termina de forma natural -> probable truncamiento."""
    core = es.rstrip()
    if not core:
        return False
    # rellena exactamente el presupuesto y corta a mitad de palabra sin signo final
    return (len(es) == len(es) and core[-1] not in ' .,!?:;…\'"') and ' ' in core

trunc, names, pend = [], [], []
for p, s in sorted(b.items()):
    t = s['text']
    if is_ident(t):
        continue
    if p in o and o[p]['text'] != t:
        en = o[p]['text']
        if natural_end(t):
            trunc.append({'pos': p, 'len': s['len'], 'en': en, 'es_actual': t})
        else:
            ew = en.split()
            if 1 < len(ew) <= 4 and all(w[:1].isupper() for w in ew if w.isalpha()) \
               and not any(c in en for c in '.!?,:;\n') and any(w.islower() and len(w) > 2 for w in t.split()):
                names.append({'pos': p, 'len': s['len'], 'en': en, 'es_actual': t})
    else:
        if len(t) >= 2 and looks_en(t):
            pend.append({'pos': p, 'len': s['len'], 'en': t})

json.dump(trunc, open(f'{OUT}/truncadas.json', 'w'), ensure_ascii=False, indent=1)
json.dump(names, open(f'{OUT}/nombres.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pend, open(f'{OUT}/pendientes.json', 'w'), ensure_ascii=False, indent=1)
print(f'truncadas={len(trunc)} nombres={len(names)} pendientes={len(pend)}')
