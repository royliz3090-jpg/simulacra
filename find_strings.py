#!/usr/bin/env python3
import re
data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/en-us.fs.decompressed', 'rb').read()
strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 4:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 4:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang)')
filtered = [x for x in strings if not skip_re.search(x['s'])]
print(f'Total strings >=4: {len(strings)}')
print(f'Filtrados (posible diálogo): {len(filtered)}')
for x in filtered[:100]:
    print('  [{}] {}'.format(x['p'], x['s']))
