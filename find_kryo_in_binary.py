#!/usr/bin/env python3
"""Buscar strings Kryo (varint + UTF-8) en archivos binarios del juego."""
import struct
import re

def find_kryo_strings(filepath, min_len=4, max_len=200):
    data = open(filepath, 'rb').read()
    print('Archivo: {} ({} bytes)'.format(filepath, len(data)))
    
    found = []
    i = 0
    while i < len(data) - 1:
        # Varint de longitud: 1 byte si < 128
        length = data[i]
        if 1 <= length <= max_len and i + 1 + length <= len(data):
            potential = data[i+1:i+1+length]
            printable = sum(1 for b in potential if 32 <= b <= 126)
            if printable == length and length >= min_len:
                s = potential.decode('ascii', errors='replace')
                # Filtrar basura
                skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|^[A-Z][a-z]{1,2}$|xsb|attribute|group|office|shape|core|image|iterator|rev|sectpr|path|password|id|auto|format|chrome|ext|ag[0-9]|[A-Z]{3,}[0-9]{2,})')
                if not skip_re.search(s):
                    # Verificar que tenga vocales (probable texto real)
                    vowel_re = re.compile(r'[aeiouAEIOU]')
                    if vowel_re.search(s):
                        found.append((i, length, s))
        i += 1
    
    print('Strings Kryo posibles: {}'.format(len(found)))
    for pos, length, s in found[:100]:
        print('  [{}] len={} {}'.format(pos, length, s))
    
    return found

# Buscar en core.binary y support.binary
find_kryo_strings('C:/IA-Prueba/SIMULACRA/extracted/core.binary')
print()
find_kryo_strings('C:/IA-Prueba/SIMULACRA/extracted/support.binary', min_len=5, max_len=100)
