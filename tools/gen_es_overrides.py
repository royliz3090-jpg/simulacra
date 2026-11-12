#!/usr/bin/env python3
"""Genera clases de UI en espanol (game27.gbeslatam.*) para el mecanismo
`Builder.overrides` del juego.

El juego original soporta idiomas cambiando clases de interfaz por otras
especificas del idioma: `GBZHCN.setup()` registra
`Builder.overrides.put(game27.gb.GBLockScreen.class, game27.gbzhcn.GBLockScreen.class)`
y asi con ~41 clases. Los textos de UI "hardcodeados" viven en esas clases.

Este script replica ese mecanismo para es-LATAM sin recompilar: toma cada clase
base del binario ORIGINAL, reescribe sus cadenas literales por las traducciones
de `translations/es-LATAM/override_ui.json` y la renombra a `game27.gbeslatam.*`.

Salida: work/build/overrides/game27/gbeslatam/**.class
y un archivo con los pares base->override para registrar en GBESLATAM.setup().

Uso:
    python3 tools/gen_es_overrides.py ORIG_CLASSES OUTDIR [--pairs-json OUT]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_patch import ClassFile  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_UI = os.path.join(HERE, "translations", "es-LATAM", "override_ui.json")

# Nombres de COLOR de fuente usados por el marcado del juego ([HANDLE], [LINK],
# [TAG]...). NO son texto visible: traducirlos rompe el coloreado y el parseo.
# El build oficial zh-cn tambien los deja igual.
FORBIDDEN_KEYS = {"HANDLE", "LINK", "TAG", "MAIL_BOLD", "MAIL_ITALIC",
                  "MAIN_GAMEPLUS", "STAT_GREEN", "boot_bold"}

# Pares base->override, copiados de GBZHCN.setup() (el mecanismo oficial de
# idioma del juego). Se incrustan aqui para no depender de fuentes externas.
OVERRIDE_PAIRS = [
    ("game27.gb.GBScreenBar", "GBScreenBar"),
    ("game27.gb.GBKeyboard", "GBKeyboard"),
    ("game27.gb.GBNotification", "GBNotification"),
    ("game27.gb.GBRebootingDialog", "GBRebootingDialog"),
    ("game27.gb.GBLockScreen", "GBLockScreen"),
    ("game27.gb.GBLockedAppDialog", "GBLockedAppDialog"),
    ("game27.gb.GBMainMenu", "GBMainMenu"),
    ("game27.gb.mail.GBMailInboxScreen", "mail.GBMailInboxScreen"),
    ("game27.gb.mail.GBMailThreadScreen", "mail.GBMailThreadScreen"),
    ("game27.gb.friends.GBFriendsCommentScreen", "friends.GBFriendsCommentScreen"),
    ("game27.gb.friends.GBFriendsLoginScreen", "friends.GBFriendsLoginScreen"),
    ("game27.gb.friends.GBFriendsProfileScreen", "friends.GBFriendsProfileScreen"),
    ("game27.gb.friends.GBFriendsWallScreen", "friends.GBFriendsWallScreen"),
    ("game27.gb.spark.GBSparkContactsScreen", "spark.GBSparkContactsScreen"),
    ("game27.gb.spark.GBSparkEditProfileScreen", "spark.GBSparkEditProfileScreen"),
    ("game27.gb.spark.GBSparkLoginScreen", "spark.GBSparkLoginScreen"),
    ("game27.gb.spark.GBSparkMatchScreen", "spark.GBSparkMatchScreen"),
    ("game27.gb.spark.GBSparkProfileScreen", "spark.GBSparkProfileScreen"),
    ("game27.gb.spark.GBSparkSuccessScreen", "spark.GBSparkSuccessScreen"),
    ("game27.gb.spark.GBSparkThreadProfileScreen", "spark.GBSparkThreadProfileScreen"),
    ("game27.gb.spark.GBSparkThreadScreen", "spark.GBSparkThreadScreen"),
    ("game27.gb.chats.GBWhatsupContactsScreen", "chats.GBWhatsupContactsScreen"),
    ("game27.gb.chats.GBWhatsupMessageThread", "chats.GBWhatsupMessageThread"),
    ("game27.gb.vloggr.GBVloggrScreen", "vloggr.GBVloggrScreen"),
    ("game27.gb.browser.GBBrowserHomeScreen", "browser.GBBrowserHomeScreen"),
    ("game27.gb.phone.GBPhoneCallScreen", "phone.GBPhoneCallScreen"),
    ("game27.gb.phone.GBPhoneContactInfoScreen", "phone.GBPhoneContactInfoScreen"),
    ("game27.gb.phone.GBPhoneContactsScreen", "phone.GBPhoneContactsScreen"),
    ("game27.gb.phone.GBPhoneDialerScreen", "phone.GBPhoneDialerScreen"),
    ("game27.gb.phone.GBPhoneFavScreen", "phone.GBPhoneFavScreen"),
    ("game27.gb.phone.GBPhoneRecentScreen", "phone.GBPhoneRecentScreen"),
    ("game27.gb.restore.GBRestoreImageScreen", "restore.GBRestoreImageScreen"),
    ("game27.gb.restore.GBRestorePhraseScreen", "restore.GBRestorePhraseScreen"),
    ("game27.gb.gallery.GBPhotoRollAlbumsScreen", "gallery.GBPhotoRollAlbumsScreen"),
    ("game27.gb.gallery.GBPhotoRollGridScreen", "gallery.GBPhotoRollGridScreen"),
    ("game27.gb.gallery.GBPhotoRollPhotoScreen", "gallery.GBPhotoRollPhotoScreen"),
    ("game27.gb.gallery.GBPhotoRollVideoScreen", "gallery.GBPhotoRollVideoScreen"),
    ("game27.gb.boot.GBBBootScreen", "boot.GBBBootScreen"),
    ("game27.gb.GBMemoryWipeDialog", "GBMemoryWipeDialog"),
    ("game27.gb.GBStatMenu", "GBStatMenu"),
    ("game27.gb.homescreen.GBHomescreen", "homescreen.GBHomescreen"),
    # Extension propia (no en GBZHCN): etiquetas de rol de los creditos.
    ("game27.gb.GBCreditsMenu", "GBCreditsMenu"),
]


def load_pairs():
    """Devuelve [(base_internal, override_internal)] en notacion de punto."""
    return [(base, "game27.gbzhcn." + ov) for base, ov in OVERRIDE_PAIRS]


def base_class_file(base_internal, classes_dir):
    return os.path.join(classes_dir, base_internal.replace(".", "/") + ".class")


def es_internal(base_internal):
    """game27.gb.spark.GBSparkThreadScreen -> game27.gbeslatam.spark.GBSparkThreadScreen"""
    parts = base_internal.split(".")
    # parts[0:2] = game27.gb ; resto = subpaquete + clase
    rest = parts[2:]
    return ".".join(["game27", "gbeslatam"] + rest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("classes_dir", help="clases del binario ORIGINAL (p.ej. /tmp/origcls)")
    ap.add_argument("outdir", help="carpeta de salida para las clases generadas")
    ap.add_argument("--ui", default=DEFAULT_UI, help="JSON de traducciones de UI")
    ap.add_argument("--pairs-json", default=None, help="donde escribir los pares base->override")
    ap.add_argument("--only", default=None, help="solo estas clases (coma-separadas, simple name)")
    ap.add_argument("--exclude", default="", help="clases base a excluir (simple names, coma-separadas)")
    ap.add_argument("--java-out", default=None, help="generar un .java con el registro de overrides")
    args = ap.parse_args()

    ui = json.load(open(args.ui, encoding="utf-8"))
    forbidden = sorted(FORBIDDEN_KEYS & set(ui))
    if forbidden:
        raise SystemExit(
            "ERROR: %s en %s no son texto traducible (nombres de color de "
            "fuente usados por el marcado). Eliminalas del mapa."
            % (forbidden, args.ui)
        )
    pairs = load_pairs()
    if args.only:
        keep = set(args.only.split(","))
        pairs = [(b, o) for b, o in pairs if b.split(".")[-1] in keep]
    if args.exclude:
        drop = set(args.exclude.split(","))
        pairs = [(b, o) for b, o in pairs if b.split(".")[-1] not in drop]

    out_pairs = []
    total = 0
    for base_internal, ov in pairs:
        bp = base_class_file(base_internal, args.classes_dir)
        if not os.path.exists(bp):
            print(f"AVISO: falta clase base {base_internal}", file=sys.stderr)
            continue
        cf = ClassFile(open(bp, "rb").read())
        n = cf.replace_strings(ui)
        if n == 0:
            continue
        new_internal = es_internal(base_internal)
        cf.rename_class(base_internal.replace(".", "/"), new_internal.replace(".", "/"))
        outpath = os.path.join(args.outdir, new_internal.replace(".", "/") + ".class")
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        open(outpath, "wb").write(cf.dump())
        out_pairs.append([base_internal, new_internal])
        total += n
        print(f"  {base_internal:45s} -> {new_internal:50s} ({n} cadenas)")

    print(f"clases generadas: {len(out_pairs)}; cadenas reescritas: {total}")
    if args.pairs_json:
        json.dump(out_pairs, open(args.pairs_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if args.java_out:
        lines = ["// GENERADO por tools/gen_es_overrides.py -- no editar a mano.",
                 "package game27.gbeslatam;", "",
                 "import sengine.utils.Builder;", "",
                 "public class GBESLATAMOverrides {",
                 "   public static void register() {"]
        for base, new in out_pairs:
            lines.append(f"      Builder.overrides.put({base}.class, {new}.class);")
        lines.append("   }")
        lines.append("}")
        open(args.java_out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print(f"registro escrito en {args.java_out}")


if __name__ == "__main__":
    main()
