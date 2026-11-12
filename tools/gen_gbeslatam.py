#!/usr/bin/env python3
"""Genera game27/gbeslatam/GBESLATAM.java a partir de GBENUS.java.

GBESLATAM.setup() publica los textos de interfaz (GlobalTexts) en espanol
latinoamericano. Se conservan intactos los identificadores, rutas, nombres
propios y cadenas estructurales (p. ej. "BUSTED", "chats://section/...",
rutas "content/...", el nombre de fuente "laborate.otf").
"""
import re
import sys
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "patch/game27/gb/GBENUS.java"
DST = pathlib.Path(__file__).resolve().parent.parent / "patch/game27/gbeslatam/GBESLATAM.java"

# var -> texto es-LATAM.  Lo que no aparezca se deja igual que en GBENUS.
T = {
    "text1": "Galería",
    "text2": "Preparando",
    "text3": "Restaurando Inicio...",
    "text4": "Restaurando Llamadas...",
    "text5": "Restaurando Chats...",
    "text6": "Restaurando Galería...",
    "text7": "Restaurando Correo...",
    "text8": "Restaurando Spark...",
    "text9": "Restaurando Jabbr...",
    "text10": "Restaurando Vloggr...",
    "text11": "Restaurando Surfer...",
    "text12": "Teléfono",
    "text13": "Chats",
    "text14": "Galería",
    "text18": "Correo",
    "text20": "Pregunta de seguridad 1/3",
    "text21": "¿Cómo se llama tu mascota?",
    "text22": "Pregunta de seguridad 2/3",
    "text23": "¿Cuál es el apellido de soltera de tu mamá?",
    "text24": "Pregunta de seguridad 3/3",
    "text25": "¿Cuál es tu película favorita?",
    "text26": "Conectando a AnnaHome-PC",
    "text29": "Trabaja en FaradaySolutions",
    "text30": "Tú también estás aquí, así que no juzgues",
    "text32": "Trabaja en Phresh Ideas",
    "text33": "La cantidad justa de torpeza",
    "text36": "CONTINUAR",
    "text37": "Bienvenido",
    "text38": "Este teléfono pertenece a:",
    "text39": "Nombre",
    "text40": "Este teléfono usa tu nombre para algunas funciones",
    "text41": "sig.",
    "text42": "Siguiente",
    "text43": "¡Hola #state:boot.name#!",
    "text44": "Para una experiencia más personalizada, responde las siguientes preguntas para ayudarnos a atenderte mejor\n\n¡No te preocupes, solo tomará un momento!",
    "text45": "Empecemos",
    "text46": "¿Cuántos años tienes?",
    "text47": "¿Cuál es tu país o región de origen?",
    "text48": "¿Eres un usuario nuevo o experimentado?",
    "text49": "Experimentado",
    "text50": "Nuevo",
    "text51": "Si es necesario, ¿prefieres configurar los ajustes manualmente o dejar que el teléfono lo haga automáticamente?",
    "text52": "Automático",
    "text53": "Manual",
    "text54": "¿Te gusta respaldar tu teléfono con frecuencia o de vez en cuando?",
    "text55": "De vez en cuando",
    "text56": "Con frecuencia",
    "text57": "¿Prefieres dormir tarde o temprano?",
    "text58": "Temprano",
    "text59": "Tarde",
    "text60": "¿Cuál es tu olor favorito?",
    "text61": "¿Qué parte de un animal prefieres comer?",
    "text62": "Costillas",
    "text63": "Muslo",
    "text64": "Cuéntame tu momento más triste de la vida.",
    "text65": "¿Te da paranoia que la cámara de tu teléfono o laptop pueda estar grabando cada uno de tus movimientos?",
    "text66": "No",
    "text67": "Sí",
    "text68": "Si todos solo pudieran decir la verdad todo el tiempo, ¿crees que el mundo sería un lugar mejor o peor?",
    "text69": "Peor",
    "text70": "Mejor",
    "text71": "¿Juras decir la verdad, toda la verdad y nada más que la verdad?",
    "text72": "¿Preferirías saber la fecha de tu muerte o la causa de tu muerte?",
    "text73": "Causa",
    "text74": "Fecha",
    "text75": "¿Preferirías perder la cabeza o todas tus extremidades?",
    "text76": "Extremidades",
    "text77": "Cabeza",
    "text78": "Si miras detrás de ti ahora mismo, ¿preferirías ver una cabeza flotante sin cuerpo o un cuerpo sin cabeza?",
    "text79": "Cuerpo sin cabeza",
    "text80": "Cabeza flotante",
    "text81": "Tu cabello huele rico.",
    "text82": "Falso",
    "text83": "Verdadero",
    "text84": "¿Puedo tocar tu cabello?",
    "text85": "No",
    "text86": "Claro",
    "text87": "Aceptas [boot_bold]entregar todos tus datos personales[] a IRIS OS para mejorar tu experiencia y otros servicios a nuestra discreción.",
    "text88": "Rechazar",
    "text89": "Aceptar",
    "text90": "Pero si sabemos más del usuario, podemos ayudarte a encontrarlo en caso de que desaparezca.\n\n¿No estás de acuerdo?",
    "text91": "Valoramos tu privacidad y no usaremos los datos de registro para ningún otro fin.",
    "text92": "Qué lástima por Anna, entonces.",
    "text93a": "¡Gracias!",
    "text93": "Tu teléfono ya está listo para usarse.\n\n¡Disfrútalo!",
    "text94": "Finalizar",
    "text95": "DEBES decirme tu nombre.",
    "text96": "Pedí TU nombre.",
    "text97": "Toby es el gato. ¡PEDÍ TU NOMBRE!",
    "text98": "No eres Greg. ¡PEDÍ TU NOMBRE!",
    "text99": "No eres Ashley. ¡PEDÍ TU NOMBRE!",
    "text100": "No eres tú, y tú no eres eso.",
    "text101": "¡PEDÍ TU NOMBRE!",
    "text102": "¡Sin groserías, IDIOTA!",
    "text103": "¡Eso no puede ser un nombre!",
    "text104": "¡Tu nombre es DEMASIADO corto!",
    "text105": "Nombre COMPLETO, por favor.",
    "text106": "DEBES decirme tu edad.",
    "text107": "Eso no es un número.",
    "text108": "Llama a tus padres u otro adulto responsable para continuar.",
    "text109": "Eso no es un número.",
    "text110": "ME dirás tu ubicación.",
    "text111": "ME dirás tu olor favorito.",
    "text112": "ME dirás tus momentos más tristes.",
    "text113": "¡TIENES que decirme más!",
    "text114": "¿ABRIR?",
    "text116": "COSA",
    "text117": "ES",
    "text118": "QUÉ",
    "text119": "ESO",
    "text120": "PARECE",
    "text121": "NADA",
    "text122": "ES",
    "text123": "QUÉ",
    "text124": "ESO",
    "text125": "PARECE",
    "text132": "Editar perfil",
    "text133": "Crear perfil",
    "text135": "Enviaste un video",
    "text136": "Enviaste una grabación de audio",
    "text137": "Enviaste una foto",
    "text138": " envió un video",
    "text139": " envió una grabación de audio",
    "text140": " envió una foto",
    "text141": "Mensaje dañado",
    "text142": "Enviaste un enlace",
    "text143": " envió un enlace",
    "text144": "Correo dañado",
    "quest1a": "Encontrar a Anna",
    "quest1": "Nuevo mensaje de Greg. Habla con él",
    "quest2": "Nuevo mensaje de Taylor. Habla con él",
    "quest3": "Intenta iniciar sesión en la app Jabbr",
    "quest4": "Greg y Anna tuvieron problemas de pareja",
    "quest5": "Anna se tomó una foto con Toby en su cumpleaños",
    "quest6": "Taylor se siente más unido a Anna ahora",
    "quest7": "Asegúrate de que Ashley nunca se entere de la desaparición de Anna",
    "quest8": "Engaña a Ashley para que revele la película favorita de Anna",
    "quest9": "Taylor quiere una foto de Anna a cambio de información",
    "quest10": "Nuevo mensaje de Ashley. Habla con ella",
    "quest11": "Consigue el código de autorización de Titan Tech",
    "quest12": "Envía el código QR a Greg",
    "quest13": "Desbloquea la tarjeta de Greg en Titan Tech",
    "quest14": "Ashley sabe que Anna está desaparecida",
    "quest15": "Investiga la casa de Anna con Greg",
    "quest16": "Averigua el cumpleaños de Toby para desbloquear los correos",
    "quest17": "Desbloquea la app Jabbr",
    "quest18": "Busca el enlace de restablecimiento de contraseña de Jabbr en el correo",
    "quest19": "Cuéntale a Greg sobre la publicación de Anna en Jabbr",
    "quest20": "Hazle saber a Greg que el teléfono está bien",
    "quest21": "Chantajea a su colega para acceder a su computadora del trabajo",
    "quest22": "Investiga los contactos de Spark de Anna",
    "quest23": "Taylor está registrado como agresor sexual",
    "quest24": "Enfrenta a Taylor por sus antecedentes penales",
    "quest25": "Ayuda a Greg a detener el borrado de memoria",
    "quest26": "Alguien intentó borrar todos los datos del teléfono de Anna",
    "quest27": "Anna encontró una nota atrevida de alguien llamado \"Yolanda\" en el teléfono de Greg",
    "quest28": "Anna encontró una prueba de embarazo no concluyente en el teléfono de Greg",
    "quest29": "Investiga los contactos de Spark de Anna",
    "quest30": "Encara a Greg por su comportamiento sospechoso",
    "quest31": "Anna conoció a alguien en Spark",
    "quest32": "Hay otro respaldo en su lugar de trabajo",
    "quest33": "Enfrenta a Yolanda por el comportamiento de Greg",
    "quest34": "Greg engañó a Anna con Yolanda",
    "quest35": "Nuevo mensaje del grupo \"BUSTED\"",
    "quest36": "Consigue el segundo respaldo en su lugar de trabajo",
    "quest37": "Denunció a Murv ante Recursos Humanos",
    "quest38": "Protegió a Murv de una investigación",
    "quest39": "Chantajea a su colega para acceder a su computadora del trabajo",
    "quest40": "Consigue el segundo respaldo en su lugar de trabajo",
    "quest41": "Todos los mensajes anteriores de Spark se han restaurado",
    "quest42": "Descubre con quién se reunió Anna en Spark restaurando sus mensajes",
    "quest43": "Crea un perfil que pueda coincidir con James",
    "quest44": "James trabajaba en Phresh Ideas",
    "quest45": "James se reunió con una celebridad de Jabbr llamada Cassie antes que con Anna",
    "quest46": "Anna se reunió con James",
    "quest47": "Averigua más sobre James a través de Cassie",
    "quest48": "Averigua más sobre James a través de su lugar de trabajo",
    "quest49": "Habla con Taylor sobre el comportamiento de James",
    "quest50": "Ashley revela que ama a Anna más que como amiga",
    "quest51": "Ashley sabe la verdad y llamó a la policía",
    "quest52": "Salva a Anna y a Taylor",
}

TAGS = {
    "Movies": "Películas",
    "Food": "Comida",
    "Books": "Libros",
    "Indoors": "Interiores",
    "Outdoors": "Aire libre",
    "Theatre": "Teatro",
    "Painting": "Pintura",
    "Moving On": "Seguir adelante",
    "Dancing": "Baile",
    "Photography": "Fotografía",
    "Personal Growth": "Crecimiento personal",
    "Health & Exercise": "Salud y ejercicio",
    "Charity": "Caridad",
    "Politics": "Política",
    "Travelling": "Viajes",
    "Pets and Animals": "Mascotas y animales",
    "Gaming": "Videojuegos",
    "Finding Love": "Encontrar el amor",
    "Casual": "Casual",
    "Work and Career": "Trabajo y carrera",
    "Music": "Música",
    "Arts and Craft": "Arte y manualidades",
    "Finance": "Finanzas",
    "Cooking": "Cocina",
    "Studies": "Estudios",
}


def main():
    src = SRC.read_text(encoding="utf-8")
    out = src.replace("package game27.gb;", "package game27.gbeslatam;")
    out = re.sub(r"\bclass GBENUS\b", "class GBESLATAM", out)
    out = out.replace("Globals.SAVE_FILENAME = Globals.SAVE_FILENAME_EN_US;",
                      "Globals.SAVE_FILENAME = Globals.SAVE_FILENAME_ES_LATAM;")

    # Reemplaza asignaciones simple:  GlobalTexts.<var> = "...";
    def repl(m):
        var = m.group(1)
        if var in T:
            return f'GlobalTexts.{var} = {json_str(T[var])};'
        return m.group(0)

    out = re.sub(r'GlobalTexts\.(\w+) = "(?:[^"\\]|\\.)*";', repl, out)

    # Traduce los elementos de arreglos de etiquetas (sparkTags / a3_*).
    for en, es in TAGS.items():
        out = out.replace(f'"{en}"', f'"{es}"')

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(out, encoding="utf-8")
    print(f"escrito {DST} ({len(out)} bytes, {out.count(chr(10))} lineas)")


def json_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


if __name__ == "__main__":
    sys.exit(main())
