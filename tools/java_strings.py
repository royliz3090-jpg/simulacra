#!/usr/bin/env python3
"""Extrae las cadenas de texto (constantes LDC) de clases Java `.class`.

Se usa para auditar el texto de UI que vive INCRUSTADO en las clases del juego
(no localizable por `.fs`). Empareja la clase en ingles (`game27/gb/GB*.class`)
con su override en espanol (`game27/gbeslatam/GB*.class`).

No requiere JDK: parsea directamente el constant pool y el bytecode.
API:
    ldc_strings(path)          -> lista ordenada de cadenas cargadas con ldc/ldc_w
    ldc_by_method(path)        -> dict {(nombre, descriptor): [cadenas]}
    utf_constants(path)        -> todas las CONSTANT_Utf8 (para buscar campos)
"""
import struct

# Longitud de operando (bytes tras el opcode). None = variable (switch/wide).
_OPERAND = {
    0x10: 1, 0x11: 2, 0x12: 1, 0x13: 2, 0x14: 2,
    0x15: 1, 0x16: 1, 0x17: 1, 0x18: 1, 0x19: 1,
    0x36: 1, 0x37: 1, 0x38: 1, 0x39: 1, 0x3a: 1,
    0x84: 2, 0xa9: 1,
    0x99: 2, 0x9a: 2, 0x9b: 2, 0x9c: 2, 0x9d: 2, 0x9e: 2, 0x9f: 2,
    0xa0: 2, 0xa1: 2, 0xa2: 2, 0xa3: 2, 0xa4: 2, 0xa5: 2, 0xa6: 2,
    0xa7: 2, 0xa8: 2,
    0xaa: None, 0xab: None, 0xc4: None,
    0xb2: 2, 0xb3: 2, 0xb4: 2, 0xb5: 2, 0xb6: 2, 0xb7: 2, 0xb8: 2,
    0xb9: 4, 0xba: 4, 0xbb: 2, 0xbc: 1, 0xbd: 2, 0xc0: 2, 0xc1: 2,
    0xc5: 3, 0xc6: 2, 0xc7: 2, 0xc8: 4, 0xc9: 4,
}


def _read_cp(data):
    if len(data) < 8 or struct.unpack_from(">I", data, 0)[0] != 0xCAFEBABE:
        return None, None
    p = 8
    count = struct.unpack_from(">H", data, p)[0]
    p += 2
    pool = [None] * count
    i = 1
    while i < count:
        tag = data[p]
        p += 1
        if tag == 1:
            ln = struct.unpack_from(">H", data, p)[0]
            p += 2
            pool[i] = ("Utf8", data[p:p + ln].decode("utf-8", "replace"))
            p += ln
        elif tag == 3:
            pool[i] = ("Int",); p += 4
        elif tag == 4:
            pool[i] = ("Float",); p += 4
        elif tag == 5:
            pool[i] = ("Long",); p += 8; i += 1
        elif tag == 6:
            pool[i] = ("Double",); p += 8; i += 1
        elif tag == 7:
            pool[i] = ("Class", struct.unpack_from(">H", data, p)[0]); p += 2
        elif tag == 8:
            pool[i] = ("String", struct.unpack_from(">H", data, p)[0]); p += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            p += 4
        elif tag == 15:
            p += 3
        elif tag == 16:
            p += 2
        elif tag in (19, 20):
            p += 2
        else:
            return None, None
        i += 1
    return pool, p


def _string_of(pool, idx):
    if idx is None or idx <= 0 or idx >= len(pool):
        return None
    e = pool[idx]
    if e and e[0] == "String":
        u = pool[e[1]] if e[1] < len(pool) else None
        if u and u[0] == "Utf8":
            return u[1]
    return None


def utf_constants(path):
    pool, _ = _read_cp(open(path, "rb").read())
    if pool is None:
        return []
    return [e[1] for e in pool if e and e[0] == "Utf8"]


def _code_of(attrs):
    for an, ab in attrs:
        if an == "Code":
            code_len = struct.unpack_from(">I", ab, 4)[0]
            return ab[8:8 + code_len]
    return None


def _ldc_walk(code, pool):
    out = []
    i = 0
    n = len(code)
    while i < n:
        op = code[i]
        if op == 0x12:  # ldc
            out.append(_string_of(pool, code[i + 1]))
            i += 2
        elif op == 0x13:  # ldc_w
            out.append(_string_of(pool, struct.unpack_from(">H", code, i + 1)[0]))
            i += 3
        elif op == 0xaa:  # tableswitch
            pad = (4 - ((i + 1) % 4)) % 4
            base = i + 1 + pad
            low = struct.unpack_from(">i", code, base + 4)[0]
            high = struct.unpack_from(">i", code, base + 8)[0]
            i = base + 12 + 4 * (high - low + 1)
        elif op == 0xab:  # lookupswitch
            pad = (4 - ((i + 1) % 4)) % 4
            base = i + 1 + pad
            npairs = struct.unpack_from(">i", code, base + 4)[0]
            i = base + 8 + 8 * npairs
        elif op == 0xc4:  # wide
            op2 = code[i + 1]
            i += 4 if op2 == 0x84 else 3
        else:
            L = _OPERAND.get(op, 0)
            i += 1 + L
    return out


def _iter_methods(path):
    data = open(path, "rb").read()
    pool, p = _read_cp(data)
    if pool is None:
        return
    p += 6  # access_flags, this_class, super_class
    ifc = struct.unpack_from(">H", data, p)[0]
    p += 2 + 2 * ifc
    nf = struct.unpack_from(">H", data, p)[0]
    p += 2
    for _ in range(nf):
        p += 6
        na = struct.unpack_from(">H", data, p)[0]
        p += 2
        for _ in range(na):
            p += 2
            ln = struct.unpack_from(">I", data, p)[0]
            p += 4 + ln
    nm = struct.unpack_from(">H", data, p)[0]
    p += 2
    for _ in range(nm):
        acc, ni, di = struct.unpack_from(">HHH", data, p)
        p += 6
        name, desc = pool[ni][1], pool[di][1]
        na = struct.unpack_from(">H", data, p)[0]
        p += 2
        attrs = []
        for _ in range(na):
            an = struct.unpack_from(">H", data, p)[0]
            p += 2
            al = struct.unpack_from(">I", data, p)[0]
            p += 4
            attrs.append((pool[an][1], data[p:p + al]))
            p += al
        yield name, desc, attrs, pool


def ldc_by_method(path):
    """dict {(nombre, descriptor): [cadenas LDC en orden de bytecode]}."""
    out = {}
    for name, desc, attrs, pool in _iter_methods(path):
        code = _code_of(attrs)
        if code is None:
            continue
        out[(name, desc)] = [s for s in _ldc_walk(code, pool) if s is not None]
    return out


def ldc_strings(path):
    out = []
    for seq in ldc_by_method(path).values():
        out.extend(seq)
    return out


if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        print(f"===== {path} =====")
        for s in ldc_strings(path):
            print("  ", repr(s))
