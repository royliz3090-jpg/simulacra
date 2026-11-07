#!/usr/bin/env python3
import re

data = open('C:/IA-Prueba/SIMULACRA/extracted/core.binary', 'rb').read()
print('core.binary: {} bytes'.format(len(data)))
print('Primeros 32 bytes hex: {}'.format(data[:32].hex()))

strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 6:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 6:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

print('Strings >= 6 en core.binary: {}'.format(len(strings)))
vowel_re = re.compile(r'[aeiouAEIOU]{2,}')
real = [x for x in strings if vowel_re.search(x['s']) and len(x['s']) >= 8]
print('Con multiples vocales: {}'.format(len(real)))
for x in real[:50]:
    print('  [{}] {}'.format(x['p'], x['s']))
