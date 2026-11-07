#!/usr/bin/env python3
"""Genera archivos de traducción para los 207 URIs identificados en SIMULACRA."""
import json
import os
from pathlib import Path

MAPPING_PATH = "C:/IA-Prueba/SIMULACRA/extracted/core_assets_extracted/en-us-uri-mapping-v2.json"
TRANS_DIR = "C:/IA-Prueba/SIMULACRA/translations/es-LATAM"

# Mapeo de categoría a directorio
CAT_DIR = {
    "dialogo_llamadas": "dialogos/llamadas",
    "chats": "dialogos/chats",
    "correo": "dialogos/correo",
    "spark": "dialogos/spark",
    "subtitulos": "subtitulos",
    "web": "web",
    "frases_restauracion": "frases_restauracion",
    "imagenes_restauracion": "imagenes_restauracion",
    "configuracion": "configuracion",
    "otro": "otro",
}


def categorizar(uri):
    if "calls/dialog" in uri:
        return "dialogo_llamadas"
    elif "/chats/" in uri:
        return "chats"
    elif "/mail/" in uri:
        return "correo"
    elif "/spark/" in uri:
        return "spark"
    elif "/subtitles/" in uri:
        return "subtitulos"
    elif "/weblayouts/" in uri or "/webpages/" in uri:
        return "web"
    elif "/restphrase/" in uri:
        return "frases_restauracion"
    elif "/restimage/" in uri:
        return "imagenes_restauracion"
    elif "/config" in uri:
        return "configuracion"
    else:
        return "otro"


def nombre_archivo(uri):
    """Genera un nombre de archivo seguro a partir del URI."""
    # Quitar prefijo en-us://
    nombre = uri.replace("en-us://", "")
    # Reemplazar caracteres no seguros para nombre de archivo
    nombre = nombre.replace("/", "_").replace("?", "_").replace(":", "_").replace("&", "_")
    return nombre + ".json"


def main():
    with open(MAPPING_PATH, encoding='utf-8') as f:
        entries = json.load(f)

    print(f"Generando archivos de traducción para {len(entries)} URIs...")

    for entry in entries:
        uri = entry["uri"]
        cat = categorizar(uri)
        dir_path = os.path.join(TRANS_DIR, CAT_DIR[cat])
        os.makedirs(dir_path, exist_ok=True)

        nombre = nombre_archivo(uri)
        file_path = os.path.join(dir_path, nombre)

        translation = {
            "uri": uri,
            "categoria": cat,
            "texto_original": None,
            "texto_traducido": None,
            "estado": "pendiente_extraccion",
            "notas": "Texto no extraído: almacenado en serialización binaria Kryo/Java. Requiere parser específico.",
            "bin2": entry.get("bin2"),
            "bin2_hex": entry.get("bin2_hex"),
            "offset4": entry.get("offset4"),
            "offset4_hex": entry.get("offset4_hex"),
            "position": entry.get("position"),
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translation, f, indent=2, ensure_ascii=False)

    print(f"Archivos generados en {TRANS_DIR}")

    # Crear archivo maestro de traducción
    maestro = {
        "juego": "SIMULACRA",
        "idioma_origen": "en-US",
        "idioma_destino": "es-LATAM",
        "total_recursos": len(entries),
        "categorias": {},
        "estado_global": "pendiente_extraccion_texto",
        "notas": "El texto real de los diálogos está en serialización Kryo/Java y no ha podido ser extraído con las herramientas disponibles.",
    }

    for entry in entries:
        cat = categorizar(entry["uri"])
        maestro["categorias"][cat] = maestro["categorias"].get(cat, 0) + 1

    maestro_path = os.path.join(TRANS_DIR, "maestro.json")
    with open(maestro_path, 'w', encoding='utf-8') as f:
        json.dump(maestro, f, indent=2, ensure_ascii=False)

    print(f"Archivo maestro guardado en {maestro_path}")
    print("Categorías:")
    for cat, count in sorted(maestro["categorias"].items()):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()