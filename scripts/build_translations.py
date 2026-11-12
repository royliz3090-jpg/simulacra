#!/usr/bin/env python3
"""
Construye translations.json para aplicar con tools/simulacra_fs.py apply.

Fuentes de traduccion (diccionarios Python en translations/es-LATAM-v2/):
  vo.py        -> VO       (clave = texto tras '=' en cadenas 'vo://...=TEXTO')
  resto.py     -> RESTO    (clave = texto completo de la cadena, sin prefijos)
  nombres.py   -> NOMBRES  (clave = texto en ingles de un nombre propio -> valor es-LATAM)

Uso:
  python3 scripts/build_translations.py <original.assets> <base.assets> <salida.json> [--strict]
"""
import sys, os, re, json, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import simulacra_fs as S

HERE = os.path.dirname(__file__)
TRDIR = os.path.join(HERE, '..', 'translations', 'es-LATAM-v2')


def load_dict(name, attr):
    path = os.path.join(TRDIR, name)
    if not os.path.exists(path):
        return {}
    spec = importlib.util.spec_from_file_location(name.replace('.py', ''), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, attr, {})


def main():
    orig = sys.argv[1] if len(sys.argv) > 1 else '/tmp/game/core.assets'
    base = sys.argv[2] if len(sys.argv) > 2 else '/tmp/baseline_core.assets'
    out = sys.argv[3] if len(sys.argv) > 3 else '/tmp/translations.json'
    strict = '--strict' in sys.argv

    VO = load_dict('vo.py', 'VO')
    RESTO = load_dict('resto.py', 'RESTO')
    NOMBRES = load_dict('nombres.py', 'NOMBRES')

    o = {s['pos']: s for s in S.scan_strings(S.load_fs(orig, 'en-us.fs')[2])}
    b = {s['pos']: s for s in S.scan_strings(S.load_fs(base, 'en-us.fs')[2])}

    entries, overflow, missing = [], [], []
    for p, s in sorted(b.items()):
        t = s['text']
        cur = o[p]['text'] if p in o else None
        new = None
        if t.startswith('vo://'):
            key = t.split('=', 1)[1] if '=' in t else None
            if key in VO:
                new = t.split('=', 1)[0] + '=' + VO[key]
        elif t.startswith('corrupted://'):
            key = t.split('=', 1)[1] if '=' in t else None
            if key in VO:
                new = t.split('=', 1)[0] + '=' + VO[key]
        else:
            if t in RESTO:
                new = RESTO[t]
            elif t in NOMBRES:
                new = NOMBRES[t]
        if new is None or new == t:
            continue
        nb = new.encode('utf-8')
        if len(nb) > s['len']:
            overflow.append((p, s['len'], len(nb), t, new))
            continue
        entries.append({'pos': p, 'len': s['len'], 'es': new})

    json.dump({'member': 'en-us.fs', 'strings': entries},
              open(out, 'w'), ensure_ascii=False, indent=1)
    print(f'aplicables={len(entries)}  no_caben={len(overflow)}  (VO={len(VO)} RESTO={len(RESTO)} NOMBRES={len(NOMBRES)})')
    if overflow:
        print('\n-- Traducciones que NO caben (acortar): --')
        for p, bl, nl, en, es in overflow[:60]:
            print(f'  @{p} budget={bl} needs={nl}  EN={en[:55]!r}  ES={es[:55]!r}')
    if strict and overflow:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
