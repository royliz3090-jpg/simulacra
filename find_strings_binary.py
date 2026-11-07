#!/usr/bin/env python3
import re

def find_strings_in_file(filepath, min_len=8):
    data = open(filepath, 'rb').read()
    print(f'Archivo: {filepath} ({len(data)} bytes)')
    
    strings = []
    current = bytearray()
    start = 0
    for i, b in enumerate(data):
        if 32 <= b <= 126:
            if not current:
                start = i
            current.append(b)
        else:
            if len(current) >= min_len:
                s = current.decode('ascii', errors='replace')
                strings.append({'s': s, 'p': start, 'l': len(s)})
            current = bytearray()
    if len(current) >= min_len:
        s = current.decode('ascii', errors='replace')
        strings.append({'s': s, 'p': start, 'l': len(s)})
    
    print(f'Total strings >= {min_len}: {len(strings)}')
    
    # Filtrar excluir URIs y nombres de clase técnicos
    skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|^[A-Z][a-z]{1,2}$|xsb|attribute|group|office|shape|core|image|iterator|rev|sectpr|path|password|id|auto|format|chrome|ext|ag[0-9])')
    
    filtered = [x for x in strings if not skip_re.search(x['s'])]
    print(f'Filtrados (posible texto real): {len(filtered)}')
    
    # Mostrar los más largos
    filtered.sort(key=lambda x: -x['l'])
    for x in filtered[:50]:
        print('  [{}] len={} {}'.format(x['p'], x['l'], x['s']))
    
    return filtered

# Buscar en core.binary y support.binary
find_strings_in_file('C:/IA-Prueba/SIMULACRA/extracted/core.binary', min_len=10)
print()
find_strings_in_file('C:/IA-Prueba/SIMULACRA/extracted/support.binary', min_len=10)
