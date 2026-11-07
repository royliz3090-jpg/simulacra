#!/usr/bin/env python3
import re

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/en-us.fs.decompressed', 'rb').read()

# Extraer todas las secuencias ASCII imprimibles >= 3 chars
strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 3:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 3:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

print('Total strings >= 3:', len(strings))

# Filtrar: excluir URIs, nombres de clase, extensiones, y strings muy técnicos
skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|^[A-Z][a-z]{1,2}$)')

filtered = [x for x in strings if not skip_re.search(x['s'])]
print('Filtrados:', len(filtered))

# Mostrar strings que parecen palabras reales (contienen vocales, no solo consonantes)
vowel_re = re.compile(r'[aeiouAEIOU]')
real_words = [x for x in filtered if vowel_re.search(x['s']) and len(x['s']) >= 4]
print('Con vocales y >= 4:', len(real_words))

for x in real_words[:200]:
    print('  [{}] {}'.format(x['p'], x['s']))
