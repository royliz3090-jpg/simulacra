"""Construye el JSON {obj: {en: es}} para apply_blob_fixes.py a partir de un
mapa global de textos, escaneando los objetos COMPRIMIDOS de un .fs."""
import sys, json
sys.path.insert(0, 'tools')
import fs_editor as E, simulacra_fs as S

fs_path, map_json, out_json = sys.argv[1:4]
mp = json.load(open(map_json, encoding='utf-8'))
mp = {fx['en']: fx['es'] for fx in mp} if isinstance(mp, list) else mp

f, objs = E.parse_fs(open(fs_path, 'rb').read())
batch = {}
for k, ob in enumerate(objs):
    if not ob['comp']:
        continue
    strs = [it['text'] for it in S.scan_strings(bytes(ob['body']))]
    hits = {t: mp[t] for t in set(strs) if t in mp and mp[t] != t}
    if hits:
        batch[str(k)] = hits

json.dump(batch, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('objetos con fixes:', len(batch),
      '| cadenas:', sum(len(v) for v in batch.values()))
