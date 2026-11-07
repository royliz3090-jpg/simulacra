#!/usr/bin/env python3
import re
import sys

# Set stdout encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/web.fs.decompressed', 'rb').read()
text = data.decode('ascii', errors='replace')

# Look for HTML-like tags
html_tags = re.findall(r'<[^>]+>', text)
if html_tags:
    print('HTML tags found: {}'.format(len(html_tags)))
    for tag in html_tags[:20]:
        print('  {}'.format(tag.encode('ascii', errors='replace').decode('ascii')))

# Look for sentences
sentences = re.findall(r'[A-Z][a-z]+(?:\s+[a-z]+){2,}', text)
print('Possible sentences: {}'.format(len(sentences)))
for s in sentences[:30]:
    print('  {}'.format(s))

# Show all strings >= 8
strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 8:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 8:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

print('\nAll strings >= 8 in web.fs:')
for x in strings[:50]:
    print('  [{}] {}'.format(x['p'], x['s']))
