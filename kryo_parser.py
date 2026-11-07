#!/usr/bin/env python3
"""
Parser Kryo para SIMULACRA - intenta extraer strings de texto de diálogo
de archivos .fs descomprimidos de LibGDX.
"""
import struct
import json
import re
from pathlib import Path

DATA_DIR = Path("C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/decompressed")
OUT_DIR = Path("C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted")


def read_varint(data, pos):
    """Lee un varint de Kryo (formato de longitud variable)."""
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
        if shift > 35:
            raise ValueError("Varint too long")
    return result, pos


def try_extract_kryo_strings(data, min_len=3, max_len=500):
    """
    Intenta extraer strings de datos serializados con Kryo.
    Busca patrones: varint de longitud + bytes UTF-8 imprimibles.
    """
    strings = []
    i = 0
    while i < len(data) - 1:
        # Intentar leer como varint de longitud
        try:
            length, new_pos = read_varint(data, i)
        except:
            i += 1
            continue

        if 1 <= length <= max_len and new_pos + length <= len(data):
            potential = data[new_pos:new_pos + length]
            printable = sum(1 for b in potential if 32 <= b <= 126 or b in (9, 10, 13))
            if printable == length and length >= min_len:
                try:
                    s = potential.decode('utf-8', errors='replace')
                except:
                    i += 1
                    continue

                # Filtrar URIs y nombres de clase técnicos
                skip_re = re.compile(
                    r'(en-us://|game27\.|com\.badlogic|java\.|sengine\.|\.ogg$|\.mp4$|\.web$|'
                    r'DialogueTree|Model\$|Serializer\$|Attribute\$|Descriptor\$|Layout|Texture|'
                    r'Sprite|Color|Font|Shader|Material|Anim|Graph|Array|Boolean|Byte|Float|'
                    r'Short|Int|String|HashMap|VoiceProfile|^[A-Z]-en-us|L[A-Z]|'
                    r'^[A-Z]engine|^[A-Z]sengine|com\.badlogic|java\.lang|^[0-9A-Fa-f]{3,}$|'
                    r'^[A-Z][a-z]{1,2}$)'
                )
                if not skip_re.search(s):
                    # Verificar que tenga vocales (probable texto real)
                    vowel_re = re.compile(r'[aeiouAEIOU]{1,}')
                    if vowel_re.search(s):
                        strings.append({
                            'position': i,
                            'length': length,
                            'string': s,
                        })
        i += 1

    return strings


def main():
    fs_path = DATA_DIR / "en-us.fs.decompressed"
    if not fs_path.exists():
        print(f"ERROR: No se encontró {fs_path}")
        return

    print(f"Leyendo {fs_path}...")
    data = fs_path.read_bytes()
    print(f"Tamaño: {len(data)} bytes")

    strings = try_extract_kryo_strings(data, min_len=3, max_len=500)
    print(f"\nStrings Kryo posibles (texto real): {len(strings)}")

    # Guardar resultados
    out_path = OUT_DIR / "en-us-kryo-strings.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(strings, f, indent=2, ensure_ascii=False)
    print(f"Guardado en {out_path}")

    # Mostrar los primeros 100
    for s in strings[:100]:
        print(f"  [{s['position']}] len={s['length']} {s['string']}")


if __name__ == '__main__':
    main()
