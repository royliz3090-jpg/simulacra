#!/usr/bin/env python3
"""Intentar parsear core.binary como datos serializados Kryo."""
import struct
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = open('C:/IA-Prueba/SIMULACRA/extracted/core.binary', 'rb').read()
print('core.binary: {} bytes'.format(len(data)))
print('Magic: {}'.format(data[:4]))

# KCB1 header - try to understand the structure
# Bytes 0-3: "KCB1"
# Bytes 4-7: 0x00000427 = 1063
# Bytes 8-11: 0x00728b87
# Bytes 12-15: 0x00007c85

# Try to find Kryo serialization patterns in core.binary
# Look for: varint length + UTF-8 text that forms words

def read_varint(data, pos):
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, pos

# Search for potential Kryo strings
found_strings = []
i = 0
while i < len(data) - 2:
    length, new_pos = read_varint(data, i)
    if 3 <= length <= 200 and new_pos + length <= len(data):
        potential = data[new_pos:new_pos + length]
        printable = sum(1 for b in potential if 32 <= b <= 126 or b in (9, 10, 13))
        if printable == length and length >= 3:
            try:
                s = potential.decode('utf-8', errors='replace')
            except:
                i += 1
                continue
            
            # Filter out random/technical strings
            skip_re = re.compile(
                r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|'
                r'DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|'
                r'Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|'
                r'Short|Int|String|HashMap|VoiceProfile|^[0-9A-Fa-f]{3,}$|'
                r'xsb|attribute|group|office|shape|core|image|iterator|rev|sectpr|'
                r'path|password|id|auto|format|chrome|ext|ag[0-9]|'
                r'com\.badlogic|java\.lang|sengine\.mass)'
            )
            if not skip_re.search(s):
                vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
                if vowel_re.search(s):
                    found_strings.append({'pos': i, 'len': length, 's': s})
    i += 1

print('\nStrings Kryo posibles en core.binary: {}'.format(len(found_strings)))
for x in found_strings[:50]:
    print('  [{}] len={} {}'.format(x['pos'], x['len'], x['s']))
