#!/usr/bin/env python3
"""
Parser para extraer texto de archivos .fs de SIMULACRA (LibGDX FileSystem + zlib).
Intenta parsear la serialización Kryo/Java para extraer cadenas de texto de diálogo.
"""
import struct
import zlib
import json
import re
import sys
from pathlib import Path

FS_DIR = Path("C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed")
OUT_DIR = Path("C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def read_decompressed(fs_path):
    """Lee un archivo ya descomprimido."""
    return fs_path.read_bytes()


def extract_uris(data):
    """Extrae todas las entradas URI del archivo descomprimido."""
    uri_prefix = b"en-us://"
    entries = []
    i = 0
    while i < len(data) - len(uri_prefix):
        if data[i:i+len(uri_prefix)] == uri_prefix:
            uri_start = i
            # Encontrar fin del URI (byte nulo)
            uri_end = i
            while uri_end < len(data) and data[uri_end] != 0:
                uri_end += 1
            uri = data[uri_start:uri_end].decode('ascii', errors='replace')

            # Saltar terminadores nulos
            pos = uri_end + 1
            if pos < len(data) and data[pos] == 0:
                pos += 1

            # Leer 2 bytes binarios + 4 bytes offset
            bin2 = 0
            offset4 = 0
            if pos + 6 <= len(data):
                bin2 = struct.unpack_from('<H', data, pos)[0]
                offset4 = struct.unpack_from('<I', data, pos + 2)[0]

            entries.append({
                'uri': uri,
                'bin2': bin2,
                'bin2_hex': f"0x{bin2:04X}",
                'offset4': offset4,
                'offset4_hex': f"0x{offset4:08X}",
                'position': uri_start,
            })
            i = uri_end + 1
        else:
            i += 1
    return entries


def find_readable_strings(data, min_length=6):
    """Encuentra cadenas ASCII legibles en los datos binarios."""
    strings = []
    current = bytearray()
    start_pos = 0
    for i, b in enumerate(data):
        if 32 <= b <= 126:  # ASCII imprimible
            if not current:
                start_pos = i
            current.append(b)
        else:
            if len(current) >= min_length:
                s = current.decode('ascii', errors='replace')
                strings.append({
                    'string': s,
                    'position': start_pos,
                    'length': len(s),
                })
            current = bytearray()
    if len(current) >= min_length:
        s = current.decode('ascii', errors='replace')
        strings.append({
            'string': s,
            'position': start_pos,
            'length': len(s),
        })
    return strings


def main():
    fs_path = FS_DIR / "en-us.fs.decompressed"
    if not fs_path.exists():
        print(f"ERROR: No se encontró {fs_path}")
        sys.exit(1)

    print(f"Leyendo {fs_path}...")
    data = read_decompressed(fs_path)
    print(f"Tamaño descomprimido: {len(data)} bytes")

    # Extraer URIs
    entries = extract_uris(data)
    print(f"URIs encontradas: {len(entries)}")

    # Guardar mapeo de URIs
    mapping_path = OUT_DIR / "en-us-uri-mapping-v2.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Mapeo guardado en {mapping_path}")

    # Encontrar strings legibles
    strings = find_readable_strings(data, min_length=8)
    print(f"Strings legibles (>=8 chars): {len(strings)}")

    # Filtrar strings que no sean URIs ni nombres de clase
    filtered = []
    skip_patterns = [
        'en-us://', 'game27.', 'com.badlogic', 'java.', 'sengine.',
        '.ogg', '.mp4', '.web', 'DialogueTree', 'Model$', 'Serializer$',
        'Attribute$', 'Descriptor$', 'Layout', 'Texture', 'Sprite',
        'Color', 'Font', 'Shader', 'Material', 'Anim', 'Graph',
        'Array', 'Boolean', 'Byte', 'Float', 'Short', 'Int',
        'String', 'HashMap', 'VoiceProfile', 'Rest', 'User',
        'Post', 'Sender', 'Contact', 'Comment', 'Content',
        'Conversation', 'Phone', 'Mail', 'Profile',
        'com.badlogic', 'java.lang', 'L[A-Z]',
    ]
    import re
    for s in strings:
        text = s['string']
        skip = False
        for p in skip_patterns:
            if p in text or re.search(p, text):
                skip = True
                break
        if not skip and len(text) >= 8:
            filtered.append(s)

    print(f"Strings filtrados (posible texto de diálogo): {len(filtered)}")

    # Guardar strings filtrados
    strings_path = OUT_DIR / "en-us-readable-strings.json"
    with open(strings_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    print(f"Strings guardados en {strings_path}")

    # Mostrar los primeros 50
    print("\n--- Primeros 50 strings filtrados ---")
    for s in filtered[:50]:
        print(f"  [{s['position']}] {s['string']}")

    # Categorizar URIs
    categories = {}
    for e in entries:
        uri = e['uri']
        if 'calls/dialog' in uri:
            cat = 'dialogo_llamadas'
        elif '/chats/' in uri:
            cat = 'chats'
        elif '/mail/' in uri:
            cat = 'correo'
        elif '/spark/' in uri:
            cat = 'spark'
        elif '/subtitles/' in uri:
            cat = 'subtitulos'
        elif '/weblayouts/' in uri or '/webpages/' in uri:
            cat = 'web'
        elif '/restphrase/' in uri:
            cat = 'frases_restauracion'
        elif '/restimage/' in uri:
            cat = 'imagenes_restauracion'
        elif '/config' in uri:
            cat = 'configuracion'
        else:
            cat = 'otro'
        categories[cat] = categories.get(cat, 0) + 1

    print("\n--- Categorías de URI ---")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()