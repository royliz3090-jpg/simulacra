#!/usr/bin/env python3
import struct

data = open('C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed/en-us.fs.decompressed', 'rb').read()

# Encontrar todas las posiciones de URI
uri_prefix = b'en-us://'
uri_positions = []
i = 0
while i < len(data) - len(uri_prefix):
    if data[i:i+len(uri_prefix)] == uri_prefix:
        uri_end = i
        while uri_end < len(data) and data[uri_end] != 0:
            uri_end += 1
        uri_positions.append((i, uri_end))
        i = uri_end + 1
    else:
        i += 1

print(f'URIs: {len(uri_positions)}')

# Buscar gaps entre URIs que puedan contener datos serializados
print('\nGaps entre URIs (posibles datos serializados):')
for idx in range(len(uri_positions) - 1):
    curr_end = uri_positions[idx][1]
    next_start = uri_positions[idx + 1][0]
    gap = next_start - curr_end
    if gap > 20:  # Gap significativo
        # Saltar los bytes de encabezado (\x00\x00 + 6 bytes)
        data_start = curr_end + 8
        data_len = next_start - data_start
        if data_len > 0:
            chunk = data[data_start:next_start]
            # Ver si hay caracteres imprimibles en el gap
            printable = sum(1 for b in chunk if 32 <= b <= 126)
            print(f'  Gap {idx}: pos {curr_end}-{next_start}, len={gap}, data_len={data_len}, printable={printable}')
            if printable > data_len * 0.3 and data_len > 50:
                print(f'    Dato: {chunk[:100]}')

# También verificar al final después del último URI
last_end = uri_positions[-1][1]
final_gap = len(data) - last_end
print(f'\nGap final: pos {last_end}-{len(data)}, len={final_gap}')
if final_gap > 20:
    chunk = data[last_end:len(data)]
    printable = sum(1 for b in chunk if 32 <= b <= 126)
    print(f'  Printable: {printable}/{final_gap}')
    print(f'  Dato: {chunk[:200]}')

# Buscar patrones Kryo: en Kryo, los objetos empiezan con un byte de clase
# Buscar secuencias de bytes que podrían ser strings Kryo (varint + UTF-8)
print('\nBuscando posibles strings Kryo (varint + texto):')
i = 0
kryo_strings = []
while i < len(data) - 2:
    # Un string Kryo: varint de longitud (1 byte si < 128) + bytes UTF-8
    length = data[i]
    if 1 <= length <= 200 and length < len(data) - i - 1:
        # Verificar si los siguientes bytes son ASCII imprimibles
        potential = data[i+1:i+1+length]
        printable_count = sum(1 for b in potential if 32 <= b <= 126)
        if printable_count == length and length >= 5:
            s = potential.decode('ascii', errors='replace')
            # Filtrar nombres de clase y URIs
            import re
            if not re.search(r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|Serializer|Attribute|Descriptor|Layout|Texture|Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|Short|Int|String|HashMap|VoiceProfile)', s):
                kryo_strings.append((i, length, s))
                if len(kryo_strings) <= 50:
                    print(f'  [{i}] len={length} {s}')
    i += 1

print(f'\nTotal strings Kryo posibles: {len(kryo_strings)}')
