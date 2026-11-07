#!/usr/bin/env python3
import re

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/content.fs.decompressed', 'rb').read()
print('content.fs.decompressed: {} bytes'.format(len(data)))

# Extract all ASCII strings >= 4 chars
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

print('Total strings >= 4: {}'.format(len(strings)))

# Show strings that look like dialogue (contain spaces, vowels, not technical)
vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
skip_re = re.compile(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|^[A-Z][a-z]{1,2}$|xsb|attribute|group|office|shape|core|image|iterator|rev|sectpr|path|password|id|auto|format|chrome|ext|ag[0-9]|\.png$|\.jpg$|\.Sprite|\.Material|\.ConfigHints|NoiseMaterial|VoiceProfile|DefaultSerializers|EnumSerializer|BooleanSerializer|ByteArraySerializer|FloatArraySerializer|FloatSerializer|DefaultArraySerializers|StringArraySerializer|IntArraySerializer|ShortArraySerializer|ObjectArraySerializer|RestPhrase|Game27|Renderer|sengine\.mass)')

dialogue = []
for x in strings:
    s = x['s']
    if not skip_re.search(s) and vowel_re.search(s) and len(s) >= 6:
        # Must contain spaces (likely a phrase) or be a common word
        if ' ' in s or len(s) >= 10:
            dialogue.append(x)

print('Posible texto de diálogo: {}'.format(len(dialogue)))
for x in dialogue[:100]:
    print('  [{}] len={} {}'.format(x['p'], x['l'], x['s']))
