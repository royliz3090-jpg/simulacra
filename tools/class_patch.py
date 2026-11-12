#!/usr/bin/env python3
"""Parchea constantes de un .class de Java SIN recompilar.

Reescribe el constant pool (UTF8) de un archivo .class:
  - reemplaza cadenas literales (usadas por CONSTANT_String),
  - puede renombrar la clase (this_class y referencias a clases internas).

Como el resto del archivo (fields, methods, atributos) solo referencia el pool
por indice y no por offset de byte, reescribir el pool con nuevas longitudes es
seguro: se re-serializa todo el archivo y el resto queda byte-identico.

Uso como libreria:
    cp = ClassFile(open(path,'rb').read())
    cp.replace_strings({"Welcome Anna !": "Bienvenida Anna!"})
    cp.rename_class("game27/gb/GBLockScreen", "game27/gbeslatam/GBLockScreen")
    open(out,'wb').write(cp.dump())
"""
import struct


class ClassFile:
    def __init__(self, data):
        self.raw = data
        self._parse()

    def _parse(self):
        d = self.raw
        assert d[:4] == b"\xca\xfe\xba\xbe", "no es un .class"
        self.minor, self.major = struct.unpack(">HH", d[4:8])
        count = struct.unpack(">H", d[8:10])[0]
        self.pool = [None] * count  # 1-based
        i = 10
        n = 1
        while n < count:
            tag = d[i]
            if tag == 1:  # UTF8
                ln = struct.unpack(">H", d[i + 1:i + 3])[0]
                val = d[i + 3:i + 3 + ln]
                self.pool[n] = [1, val]
                i += 3 + ln
            elif tag in (7, 8, 16, 19, 20):  # Class, String, MethodType, Module, Package
                self.pool[n] = [tag, struct.unpack(">H", d[i + 1:i + 3])[0]]
                i += 3
            elif tag == 15:  # MethodHandle
                self.pool[n] = [tag, d[i + 1], struct.unpack(">H", d[i + 2:i + 4])[0]]
                i += 4
            elif tag in (3, 4):  # Integer, Float
                self.pool[n] = [tag, d[i + 1:i + 5]]
                i += 5
            elif tag in (5, 6):  # Long, Double (ocupan 2 slots)
                self.pool[n] = [tag, d[i + 1:i + 9]]
                i += 9
                n += 1
            elif tag in (9, 10, 11, 12, 17, 18):  # refs, NameAndType, Dynamic
                self.pool[n] = [tag, struct.unpack(">HH", d[i + 1:i + 5])]
                i += 5
            else:
                raise ValueError(f"tag de constant pool desconocido: {tag} en #{n}")
            n += 1
        self.pool_end = i
        self.rest = d[i:]  # fields, methods, attributes (byte-identico)

    def _utf8(self, idx):
        e = self.pool[idx]
        return e[1].decode("utf-8", "surrogateescape") if e and e[0] == 1 else None

    def _string_utf8_indices(self):
        """Indices de CONSTANT_Utf8 referenciados por un CONSTANT_String.

        Solo esos pueden tocarse: un mismo texto puede aparecer tambien como
        nombre de metodo/campo (NameAndType) y NO debe traducirse.
        """
        idx = set()
        for e in self.pool:
            if e and e[0] == 8:  # String -> Utf8
                idx.add(e[1])
        return idx

    def replace_strings(self, mapping):
        """Reemplaza valores de CONSTANT_Utf8 usados como cadena literal."""
        allowed = self._string_utf8_indices()
        changed = 0
        for n, e in enumerate(self.pool):
            if e and e[0] == 1 and n in allowed:
                try:
                    s = e[1].decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if s in mapping:
                    e[1] = mapping[s].encode("utf-8")
                    changed += 1
        return changed

    def rename_class(self, old_internal, new_internal):
        """Renombra la clase (this_class) y sus referencias internas.

        old/new en notacion interna (p.ej. 'game27/gb/GBLockScreen').
        Reemplaza el nombre exacto, el de sus clases internas (old$X -> new$X)
        y el descriptor de tipo (Lold; -> Lnew;), que aparece en firmas
        genericas (atributo Signature) y debe coincidir con el nombre real.
        """
        old_desc = "L" + old_internal + ";"
        new_desc = "L" + new_internal + ";"
        changed = 0
        for e in self.pool:
            if e and e[0] == 1:
                try:
                    s = e[1].decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if s == old_internal:
                    e[1] = new_internal.encode("utf-8")
                    changed += 1
                elif s.startswith(old_internal + "$"):
                    e[1] = (new_internal + s[len(old_internal):]).encode("utf-8")
                    changed += 1
                elif s == old_desc:
                    e[1] = new_desc.encode("utf-8")
                    changed += 1
        return changed

    def dump(self):
        out = bytearray()
        out += b"\xca\xfe\xba\xbe"
        out += struct.pack(">HH", self.minor, self.major)
        out += struct.pack(">H", len(self.pool))
        for n in range(1, len(self.pool)):
            e = self.pool[n]
            if e is None:
                continue  # slot de Long/Double
            tag = e[0]
            if tag == 1:
                out += bytes([1]) + struct.pack(">H", len(e[1])) + e[1]
            elif tag in (7, 8, 16, 19, 20):
                out += bytes([tag]) + struct.pack(">H", e[1])
            elif tag == 15:
                out += bytes([tag, e[1]]) + struct.pack(">H", e[2])
            elif tag in (3, 4):
                out += bytes([tag]) + e[1]
            elif tag in (5, 6):
                out += bytes([tag]) + e[1]
            elif tag in (9, 10, 11, 12, 17, 18):
                out += bytes([tag]) + struct.pack(">HH", e[1][0], e[1][1])
            else:
                raise ValueError(f"tag desconocido al serializar: {tag}")
        out += self.rest
        return bytes(out)

    def string_literals(self):
        """Devuelve las cadenas literales (CONSTANT_String -> Utf8)."""
        out = []
        for e in self.pool:
            if e and e[0] == 8:
                s = self._utf8(e[1])
                if s is not None:
                    out.append(s)
        return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cf = ClassFile(open(sys.argv[1], "rb").read())
    for s in cf.string_literals():
        print(repr(s))
