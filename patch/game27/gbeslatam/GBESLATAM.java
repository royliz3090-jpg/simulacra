package game27.gbeslatam;

import game27.GlobalTexts;
import game27.Globals;
import java.util.Locale;

public class GBESLATAM {
   /** Teclado con el placeholder del autocompletado en espanol. */
   public static game27.Keyboard newKeyboard() {
      return new GBESLATAMKeyboard();
   }

   public static void setup() {
      // Sustituye las clases de UI con textos hardcodeados por sus variantes
      // en espanol (game27.gbeslatam.*), igual que hace GBZHCN para zh-cn.
      GBESLATAMOverrides.register();
      Globals.SAVE_FILENAME = Globals.SAVE_FILENAME_ES_LATAM;
      Globals.timeLocale = Locale.US;
      Globals.timeLocaleCustomAMPM = new String[]{"am", "pm"};
      Globals.googleConfigID = "15bt57v9AhyK8-USYGIoE7evyoREUGWicURmaFrMFE9I";
      Globals.dialogueTreeMaxCharsPerWord = 10.0F;
      GlobalTexts.text1 = "Galería";
      GlobalTexts.text2 = "Preparando";
      GlobalTexts.text3 = "Restaurando Inicio...";
      GlobalTexts.text4 = "Restaurando Llamadas...";
      GlobalTexts.text5 = "Restaurando Chats...";
      GlobalTexts.text6 = "Restaurando Galería...";
      GlobalTexts.text7 = "Restaurando Correo...";
      GlobalTexts.text8 = "Restaurando Spark...";
      GlobalTexts.text9 = "Restaurando Jabbr...";
      GlobalTexts.text10 = "Restaurando Vloggr...";
      GlobalTexts.text11 = "Restaurando Surfer...";
      GlobalTexts.text12 = "Teléfono";
      GlobalTexts.text13 = "Chats";
      GlobalTexts.text14 = "Galería";
      GlobalTexts.text15 = "Spark";
      GlobalTexts.text16 = "Vloggr";
      GlobalTexts.text17 = "Surfer";
      GlobalTexts.text18 = "Correo";
      GlobalTexts.text19 = "Jabbr";
      GlobalTexts.text20 = "Pregunta de seguridad 1/3";
      GlobalTexts.text21 = "¿Cómo se llama tu mascota?";
      GlobalTexts.text22 = "Pregunta de seguridad 2/3";
      GlobalTexts.text23 = "¿Cuál es el apellido de soltera de tu mamá?";
      GlobalTexts.text24 = "Pregunta de seguridad 3/3";
      GlobalTexts.text25 = "¿Cuál es tu película favorita?";
      GlobalTexts.text26 = "Conectando a AnnaHome-PC";
      GlobalTexts.text27 = "Phill";
      GlobalTexts.text28 = "Anna";
      GlobalTexts.text29 = "Trabaja en FaradaySolutions";
      GlobalTexts.text30 = "Tú también estás aquí, así que no juzgues";
      GlobalTexts.text31 = "James";
      GlobalTexts.text32 = "Trabaja en Phresh Ideas";
      GlobalTexts.text33 = "La cantidad justa de torpeza";
      GlobalTexts.text34 = "BUSTED";
      GlobalTexts.text35 = "chats://section/Taylor se desconecto";
      GlobalTexts.text36 = "CONTINUAR";
      GlobalTexts.text37 = "Bienvenido";
      GlobalTexts.text38 = "Este teléfono pertenece a:";
      GlobalTexts.text39 = "Nombre";
      GlobalTexts.text40 = "Este teléfono usa tu nombre para algunas funciones";
      GlobalTexts.text41 = "sig.";
      GlobalTexts.text42 = "Siguiente";
      GlobalTexts.text43 = "¡Hola #state:boot.name#!";
      GlobalTexts.text44 = "Para una experiencia más personalizada, responde las siguientes preguntas para ayudarnos a atenderte mejor\n\n¡No te preocupes, solo tomará un momento!";
      GlobalTexts.text45 = "Empecemos";
      GlobalTexts.text46 = "¿Cuántos años tienes?";
      GlobalTexts.text47 = "¿Cuál es tu país o región de origen?";
      GlobalTexts.text48 = "¿Eres un usuario nuevo o experimentado?";
      GlobalTexts.text49 = "Experimentado";
      GlobalTexts.text50 = "Nuevo";
      GlobalTexts.text51 = "Si es necesario, ¿prefieres configurar los ajustes manualmente o dejar que el teléfono lo haga automáticamente?";
      GlobalTexts.text52 = "Automático";
      GlobalTexts.text53 = "Manual";
      GlobalTexts.text54 = "¿Te gusta respaldar tu teléfono con frecuencia o de vez en cuando?";
      GlobalTexts.text55 = "De vez en cuando";
      GlobalTexts.text56 = "Con frecuencia";
      GlobalTexts.text57 = "¿Prefieres dormir tarde o temprano?";
      GlobalTexts.text58 = "Temprano";
      GlobalTexts.text59 = "Tarde";
      GlobalTexts.text60 = "¿Cuál es tu olor favorito?";
      GlobalTexts.text61 = "¿Qué parte de un animal prefieres comer?";
      GlobalTexts.text62 = "Costillas";
      GlobalTexts.text63 = "Muslo";
      GlobalTexts.text64 = "Cuéntame tu momento más triste de la vida.";
      GlobalTexts.text65 = "¿Te da paranoia que la cámara de tu teléfono o laptop pueda estar grabando cada uno de tus movimientos?";
      GlobalTexts.text66 = "No";
      GlobalTexts.text67 = "Sí";
      GlobalTexts.text68 = "Si todos solo pudieran decir la verdad todo el tiempo, ¿crees que el mundo sería un lugar mejor o peor?";
      GlobalTexts.text69 = "Peor";
      GlobalTexts.text70 = "Mejor";
      GlobalTexts.text71 = "¿Juras decir la verdad, toda la verdad y nada más que la verdad?";
      GlobalTexts.text72 = "¿Preferirías saber la fecha de tu muerte o la causa de tu muerte?";
      GlobalTexts.text73 = "Causa";
      GlobalTexts.text74 = "Fecha";
      GlobalTexts.text75 = "¿Preferirías perder la cabeza o todas tus extremidades?";
      GlobalTexts.text76 = "Extremidades";
      GlobalTexts.text77 = "Cabeza";
      GlobalTexts.text78 = "Si miras detrás de ti ahora mismo, ¿preferirías ver una cabeza flotante sin cuerpo o un cuerpo sin cabeza?";
      GlobalTexts.text79 = "Cuerpo sin cabeza";
      GlobalTexts.text80 = "Cabeza flotante";
      GlobalTexts.text81 = "Tu cabello huele rico.";
      GlobalTexts.text82 = "Falso";
      GlobalTexts.text83 = "Verdadero";
      GlobalTexts.text84 = "¿Puedo tocar tu cabello?";
      GlobalTexts.text85 = "No";
      GlobalTexts.text86 = "Claro";
      GlobalTexts.text87 = "Aceptas [boot_bold]entregar todos tus datos personales[] a IRIS OS para mejorar tu experiencia y otros servicios a nuestra discreción.";
      GlobalTexts.text88 = "Rechazar";
      GlobalTexts.text89 = "Aceptar";
      GlobalTexts.text90 = "Pero si sabemos más del usuario, podemos ayudarte a encontrarlo en caso de que desaparezca.\n\n¿No estás de acuerdo?";
      GlobalTexts.text91 = "Valoramos tu privacidad y no usaremos los datos de registro para ningún otro fin.";
      GlobalTexts.text92 = "Qué lástima por Anna, entonces.";
      GlobalTexts.text93a = "¡Gracias!";
      GlobalTexts.text93 = "Tu teléfono ya está listo para usarse.\n\n¡Disfrútalo!";
      GlobalTexts.text94 = "Finalizar";
      GlobalTexts.text95 = "DEBES decirme tu nombre.";
      GlobalTexts.text96 = "Pedí TU nombre.";
      GlobalTexts.text97 = "Toby es el gato. ¡PEDÍ TU NOMBRE!";
      GlobalTexts.text98 = "No eres Greg. ¡PEDÍ TU NOMBRE!";
      GlobalTexts.text99 = "No eres Ashley. ¡PEDÍ TU NOMBRE!";
      GlobalTexts.text100 = "No eres tú, y tú no eres eso.";
      GlobalTexts.text101 = "¡PEDÍ TU NOMBRE!";
      GlobalTexts.text102 = "¡Sin groserías, IDIOTA!";
      GlobalTexts.text103 = "¡Eso no puede ser un nombre!";
      GlobalTexts.text104 = "¡Tu nombre es DEMASIADO corto!";
      GlobalTexts.text105 = "Nombre COMPLETO, por favor.";
      GlobalTexts.text106 = "DEBES decirme tu edad.";
      GlobalTexts.text107 = "Eso no es un número.";
      GlobalTexts.text108 = "Llama a tus padres u otro adulto responsable para continuar.";
      GlobalTexts.text109 = "Eso no es un número.";
      GlobalTexts.text110 = "ME dirás tu ubicación.";
      GlobalTexts.text111 = "ME dirás tu olor favorito.";
      GlobalTexts.text112 = "ME dirás tus momentos más tristes.";
      GlobalTexts.text113 = "¡TIENES que decirme más!";
      GlobalTexts.text114 = "¿ABRIR?";
      GlobalTexts.text115 = "NO";
      GlobalTexts.text116 = "COSA";
      GlobalTexts.text117 = "ES";
      GlobalTexts.text118 = "QUÉ";
      GlobalTexts.text119 = "ESO";
      GlobalTexts.text120 = "PARECE";
      GlobalTexts.text121 = "NADA";
      GlobalTexts.text122 = "ES";
      GlobalTexts.text123 = "QUÉ";
      GlobalTexts.text124 = "ESO";
      GlobalTexts.text125 = "PARECE";
      GlobalTexts.text126 = "content/spark/james-swipe1.jpg";
      GlobalTexts.text127 = "content/spark/james-swipe2.jpg";
      GlobalTexts.text128 = "content/spark/james-swipe3.jpg";
      GlobalTexts.text129 = "content/spark/james-swipe4.jpg";
      GlobalTexts.text130 = "content/spark/james-swipe5.jpg";
      GlobalTexts.text131 = "content/spark/james-swipe6.jpg";
      GlobalTexts.text132 = "Editar perfil";
      GlobalTexts.text133 = "Crear perfil";
      GlobalTexts.text134 = "laborate.otf";
      GlobalTexts.text135 = "Enviaste un video";
      GlobalTexts.text136 = "Enviaste una grabación de audio";
      GlobalTexts.text137 = "Enviaste una foto";
      GlobalTexts.text138 = " envió un video";
      GlobalTexts.text139 = " envió una grabación de audio";
      GlobalTexts.text140 = " envió una foto";
      GlobalTexts.text141 = "Mensaje dañado";
      GlobalTexts.text142 = "Enviaste un enlace";
      GlobalTexts.text143 = " envió un enlace";
      GlobalTexts.text144 = "Correo dañado";
      GlobalTexts.text145 = null;
      GlobalTexts.text146 = null;
      GlobalTexts.text147 = null;
      GlobalTexts.text148 = null;
      GlobalTexts.text149 = null;
      GlobalTexts.text150 = null;
      GlobalTexts.quest1a = "Encontrar a Anna";
      GlobalTexts.quest1 = "Nuevo mensaje de Greg. Habla con él";
      GlobalTexts.quest2 = "Nuevo mensaje de Taylor. Habla con él";
      GlobalTexts.quest3 = "Intenta iniciar sesión en la app Jabbr";
      GlobalTexts.quest4 = "Greg y Anna tuvieron problemas de pareja";
      GlobalTexts.quest5 = "Anna se tomó una foto con Toby en su cumpleaños";
      GlobalTexts.quest6 = "Taylor se siente más unido a Anna ahora";
      GlobalTexts.quest7 = "Asegúrate de que Ashley nunca se entere de la desaparición de Anna";
      GlobalTexts.quest8 = "Engaña a Ashley para que revele la película favorita de Anna";
      GlobalTexts.quest9 = "Taylor quiere una foto de Anna a cambio de información";
      GlobalTexts.quest10 = "Nuevo mensaje de Ashley. Habla con ella";
      GlobalTexts.quest11 = "Consigue el código de autorización de Titan Tech";
      GlobalTexts.quest12 = "Envía el código QR a Greg";
      GlobalTexts.quest13 = "Desbloquea la tarjeta de Greg en Titan Tech";
      GlobalTexts.quest14 = "Ashley sabe que Anna está desaparecida";
      GlobalTexts.quest15 = "Investiga la casa de Anna con Greg";
      GlobalTexts.quest16 = "Averigua el cumpleaños de Toby para desbloquear los correos";
      GlobalTexts.quest17 = "Desbloquea la app Jabbr";
      GlobalTexts.quest18 = "Busca el enlace de restablecimiento de contraseña de Jabbr en el correo";
      GlobalTexts.quest19 = "Cuéntale a Greg sobre la publicación de Anna en Jabbr";
      GlobalTexts.quest20 = "Hazle saber a Greg que el teléfono está bien";
      GlobalTexts.quest21 = "Chantajea a su colega para acceder a su computadora del trabajo";
      GlobalTexts.quest22 = "Investiga los contactos de Spark de Anna";
      GlobalTexts.quest23 = "Taylor está registrado como agresor sexual";
      GlobalTexts.quest24 = "Enfrenta a Taylor por sus antecedentes penales";
      GlobalTexts.quest25 = "Ayuda a Greg a detener el borrado de memoria";
      GlobalTexts.quest26 = "Alguien intentó borrar todos los datos del teléfono de Anna";
      GlobalTexts.quest27 = "Anna encontró una nota atrevida de alguien llamado \"Yolanda\" en el teléfono de Greg";
      GlobalTexts.quest28 = "Anna encontró una prueba de embarazo no concluyente en el teléfono de Greg";
      GlobalTexts.quest29 = "Investiga los contactos de Spark de Anna";
      GlobalTexts.quest30 = "Encara a Greg por su comportamiento sospechoso";
      GlobalTexts.quest31 = "Anna conoció a alguien en Spark";
      GlobalTexts.quest32 = "Hay otro respaldo en su lugar de trabajo";
      GlobalTexts.quest33 = "Enfrenta a Yolanda por el comportamiento de Greg";
      GlobalTexts.quest34 = "Greg engañó a Anna con Yolanda";
      GlobalTexts.quest35 = "Nuevo mensaje del grupo \"BUSTED\"";
      GlobalTexts.quest36 = "Consigue el segundo respaldo en su lugar de trabajo";
      GlobalTexts.quest37 = "Denunció a Murv ante Recursos Humanos";
      GlobalTexts.quest38 = "Protegió a Murv de una investigación";
      GlobalTexts.quest39 = "Chantajea a su colega para acceder a su computadora del trabajo";
      GlobalTexts.quest40 = "Consigue el segundo respaldo en su lugar de trabajo";
      GlobalTexts.quest41 = "Todos los mensajes anteriores de Spark se han restaurado";
      GlobalTexts.quest42 = "Descubre con quién se reunió Anna en Spark restaurando sus mensajes";
      GlobalTexts.quest43 = "Crea un perfil que pueda coincidir con James";
      GlobalTexts.quest44 = "James trabajaba en Phresh Ideas";
      GlobalTexts.quest45 = "James se reunió con una celebridad de Jabbr llamada Cassie antes que con Anna";
      GlobalTexts.quest46 = "Anna se reunió con James";
      GlobalTexts.quest47 = "Averigua más sobre James a través de Cassie";
      GlobalTexts.quest48 = "Averigua más sobre James a través de su lugar de trabajo";
      GlobalTexts.quest49 = "Habla con Taylor sobre el comportamiento de James";
      GlobalTexts.quest50 = "Ashley revela que ama a Anna más que como amiga";
      GlobalTexts.quest51 = "Ashley sabe la verdad y llamó a la policía";
      GlobalTexts.quest52 = "Salva a Anna y a Taylor";
      GlobalTexts.quest53 = null;
      GlobalTexts.quest54 = null;
      GlobalTexts.quest55 = null;
      GlobalTexts.quest56 = null;
      GlobalTexts.quest57 = null;
      GlobalTexts.quest58 = null;
      GlobalTexts.quest59 = null;
      GlobalTexts.quest60 = null;
      GlobalTexts.a3_james_tags_required = new String[]{"Seguir adelante", "Encontrar el amor"};
      GlobalTexts.a3_james_tags_optional = new String[]{
         "Películas", "Libros", "Interiores", "Crecimiento personal", "Mascotas y animales", "Videojuegos", "Trabajo y carrera", "Música", "Estudios", "Viajes"
      };
      GlobalTexts.sparkTags = new String[]{
         "Películas",
         "Comida",
         "Libros",
         "Interiores",
         "Aire libre",
         "Teatro",
         "Pintura",
         "Seguir adelante",
         "Baile",
         "Fotografía",
         "Crecimiento personal",
         "Salud y ejercicio",
         "Caridad",
         "Política",
         "Viajes",
         "Mascotas y animales",
         "Videojuegos",
         "Encontrar el amor",
         "Casual",
         "Trabajo y carrera",
         "Música",
         "Arte y manualidades",
         "Finanzas",
         "Cocina",
         "Estudios"
      };
      Globals.corruptedMessageWordMaxLength = 10;
   }
}
