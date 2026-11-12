#!/usr/bin/env python3
"""Restaura identificadores internos del juego en un `.fs` traducido.

Problema (ver docs/ESTADO_TRADUCCION.md): parte del texto del `.fs` NO es texto
visible, sino CLAVES internas que el codigo del juego compara o usa para buscar
recursos (p. ej. el nombre de album `_Jabbr/cover`, `missed`, `incoming`,
`vlog3`, `center`, `Camera`...). Si se traducen, el juego falla al cargar
(``Unable to find media _Jabbr/cover``) o muestra datos incorrectos.

Este script:
  1. Lee el `.fs` original (ingles) y el `.fs` traducido (mismo orden de
     cadenas: la cadena i del traducido corresponde a la i del original).
  2. Detecta las cadenas cuya version INGLESA pertenece al conjunto de CLAVES
     protegidas y que fueron traducidas.
  3. Reescribe esas cadenas de vuelta al ingles, recomputando los offsets del
     bloque de formato (las cadenas pueden cambiar de longitud en bytes).
  4. Reemite el `.fs` completo (cabecera + formato comprimido + datos).

Uso:
  python3 tools/fs_fix_keys.py <orig.fs> <traducido.fs> <salida.fs> [--keys claves.txt]
"""
import argparse
import re
import struct
import sys
import zlib

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import build_locale_fs as B  # noqa: E402
import simulacra_fs as S  # noqa: E402

# El juego serializa fechas en los ficheros de configuracion y las vuelve a
# parsear con SimpleDateFormat(..., Locale.US).  Si se traduce la fecha, el
# parseo falla ("Failed to parse time: ...").  Ademas las fechas se muestran
# reformateandolas con Globals.timeLocale, no leyendo el texto, asi que
# traducirlas es inutil.  Por eso se restauran al ingles.
_MESES = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec")
_DATE_PATTERNS = [
    rf"^\d{{1,2}} (?:{_MESES}) \d{{4}}, \d{{1,2}}:\d{{2}} (?:AM|PM)$",  # dd MMMM yyyy, h:mm a
    rf"^\d{{1,2}} (?:{_MESES}) \d{{4}}$",                              # dd MMMM yyyy
    rf"^\d{{1,2}} (?:{_MESES})$",                                      # d MMMM / dd MMM
    rf"^[A-Z][a-z]{{2}}, \d{{1,2}} (?:{_MESES})$",                     # EEE, d MMMM
    r"^\d{1,2}:\d{2} (?:AM|PM)$",                                      # h:mm a
]
_DATE_RE = re.compile("|".join(_DATE_PATTERNS))


def is_protected_date(text):
    return bool(_DATE_RE.match(text))


# Un identificador de recurso (``scheme://ruta``) nunca debe traducirse: el
# juego lo compara literalmente para localizar contenido.  Ademas de proteger
# cadenas que sean *solo* un URI, hay que blindar el PREFIJO de cadenas que
# empiezan por un URI (p. ej. ``chats://section/<texto>``).
_URI_PREFIX_RE = re.compile(r"^([a-z]+://[^/]*/)")


def uri_prefix(text):
    m = _URI_PREFIX_RE.match(text)
    return m.group(1) if m else None


def parse(fs_bytes):
    fmt, data, field = B.split_fs(fs_bytes)
    f = B.parse_format(fmt)
    return f, data, field


def rebuild(f, data, edits):
    """Reemite el .fs aplicando ediciones (pos, len_viejo, bytes_nuevos).

    Cada cadena Kryo va precedida de su longitud en 4 bytes big-endian; al
    cambiar el numero de bytes hay que reescribir TAMBIEN ese prefijo o el
    scanner del juego se desincroniza y se traga la cadena siguiente.  Se
    recomputa ademas `offsets` sumando el delta de bytes insertado antes de
    cada uno.
    """
    edits = sorted(edits)
    new_data = bytearray(data)
    # aplicar de atras hacia adelante para no invalidar posiciones
    for pos, old_len, new in reversed(edits):
        new_data[pos - 4:pos + old_len] = struct.pack(">I", len(new)) + new

    # recomputar offsets: delta acumulado estrictamente antes de cada offset
    new_offsets = []
    for off in f["offsets"]:
        delta = 0
        for pos, old_len, new in edits:
            if pos < off:
                delta += len(new) - old_len
            else:
                break
        new_offsets.append(off + delta)
    f2 = dict(f)
    f2["offsets"] = new_offsets

    new_fmt = B.emit_format(f2)
    comp = zlib.compress(new_fmt, 9)
    field = (len(comp) << 1) | 1
    return b"FileSystem" + B.write_int(field) + comp + bytes(new_data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("orig")
    ap.add_argument("trans")
    ap.add_argument("out")
    ap.add_argument("--keys", default="tools/keys_protegidas.txt")
    ap.add_argument("--direct", action="store_true",
                    help="tratar los .fs como archivos crudos (no ZIP)")
    a = ap.parse_args()

    def read(p):
        # los .fs sueltos suelen ser crudos; core.assets es un ZIP
        raw = open(p, "rb").read()
        if raw[:10] == b"FileSystem":
            return raw
        import zipfile
        with zipfile.ZipFile(p) as z:
            names = z.namelist()
            member = "en-us.fs" if "en-us.fs" in names else names[0]
            return z.read(member)

    keys = set()
    with open(a.keys, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                keys.add(line)

    orig = read(a.orig)
    trans = read(a.trans)
    fo, do, _ = parse(orig)
    ft, dt, _ = parse(trans)

    so = [s for s in S.scan_strings(do)]
    st = [s for s in S.scan_strings(dt)]
    if len(so) != len(st):
        raise SystemExit(f"conteo de cadenas distinto: orig={len(so)} trans={len(st)}")

    edits = []
    restored = []
    for i in range(len(so)):
        eng = so[i]["text"]
        esp = st[i]["text"]
        if eng == esp:
            continue
        if eng in keys or is_protected_date(eng):
            pos = st[i]["pos"]
            old_len = st[i]["len"]
            edits.append((pos, old_len, eng.encode("utf-8")))
            restored.append((i, eng, esp))
            continue
        # Blindaje del prefijo de recurso: si el original empieza por
        # ``scheme://ruta/`` el traducido debe conservarlo EXACTO.
        pfx = uri_prefix(eng)
        if pfx and not esp.startswith(pfx):
            payload = esp[len(uri_prefix(esp)):] if uri_prefix(esp) else esp
            new = pfx + payload
            edits.append((st[i]["pos"], st[i]["len"], new.encode("utf-8")))
            restored.append((i, new, esp))

    print(f"claves protegidas: {len(keys)} (+ patrones de fecha)")
    print(f"cadenas restauradas a ingles: {len(restored)}")
    for i, eng, esp in restored:
        print(f"  {i}: {esp!r} -> {eng!r}")

    out = rebuild(ft, dt, edits)
    open(a.out, "wb").write(out)
    print(f"escrito {a.out}: {len(out)} bytes")


if __name__ == "__main__":
    main()
