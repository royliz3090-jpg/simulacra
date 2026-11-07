#!/usr/bin/env python3
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/main.fs.decompressed', 'rb').read()
print('main.fs.decompressed: {} bytes'.format(len(data)))

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

# Filter out technical strings
skip_re = re.compile(
    r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|'
    r'DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|'
    r'Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|'
    r'Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|'
    r'^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|'
    r'^[A-Z][a-z]{1,2}$|xsb|attribute|group|office|shape|core|image|iterator|'
    r'rev|sectpr|path|password|id|auto|format|chrome|ext|ag[0-9]|\.png$|\.jpg$|'
    r'\.Sprite|\.Material|\.ConfigHints|NoiseMaterial|VoiceProfile|'
    r'DefaultSerializers|EnumSerializer|BooleanSerializer|ByteArraySerializer|'
    r'FloatArraySerializer|FloatSerializer|DefaultArraySerializers|'
    r'StringArraySerializer|IntArraySerializer|ShortArraySerializer|'
    r'ObjectArraySerializer|RestPhrase|Game27|Renderer|sengine\.mass|'
    r'FieldSerializer|MapSerializer|PixmapKryoSerializer|TextureFilter|'
    r'TextureWrap|Pixmap|HashMap|LayoutNamespace|SimpleMaterial|'
    r'ConfigHints|MaterialAttribute|Shader|ShaderSerializer|TextureZERO|'
    r'Layout|bg-|anna-|action-|arrow-|back-|bar-|begin-|card-|chat-|'
    r'comment-|continue-|credits-|discord-|app-|Bapps|Dapps|'
    r'\.ogg\.VoiceProfile)'
)

# Show strings that might be dialogue/UI text
dialogue = []
for x in strings:
    s = x['s']
    if not skip_re.search(s):
        # Check if it looks like real text (has vowels, not just random chars)
        vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
        if vowel_re.search(s) and len(s) >= 6:
            dialogue.append(x)

print('\nPosible texto de diálogo/UI en main.fs: {}'.format(len(dialogue)))
for x in dialogue[:100]:
    print('  [{}] len={} {}'.format(x['p'], x['l'], x['s']))

# Also show ALL strings sorted by length (descending) to see the longest ones
strings.sort(key=lambda x: -x['l'])
print('\nStrings más largos en main.fs:')
for x in strings[:30]:
    print('  [{}] len={} {}'.format(x['p'], x['l'], x['s']))
