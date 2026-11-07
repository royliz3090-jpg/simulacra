#!/usr/bin/env python3
import re

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/en-us.fs.decompressed', 'rb').read()

# Buscar TODAS las secuencias ASCII imprimibles >= 5, sin filtrar agresivamente
strings = []
current = bytearray()
start = 0
for i, b in enumerate(data):
    if 32 <= b <= 126:
        if not current:
            start = i
        current.append(b)
    else:
        if len(current) >= 5:
            s = current.decode('ascii', errors='replace')
            strings.append({'s': s, 'p': start, 'l': len(s)})
        current = bytearray()
if len(current) >= 5:
    s = current.decode('ascii', errors='replace')
    strings.append({'s': s, 'p': start, 'l': len(s)})

print('Total strings >= 5:', len(strings))

# Mostrar las 100 más largas (más probable que sean texto real)
strings.sort(key=lambda x: -x['l'])
for x in strings[:100]:
    print('  [{}] len={} {}'.format(x['p'], x['l'], x['s']))
