package game27.gbeslatam;

import game27.Keyboard;

/**
 * Teclado con los textos de ayuda en es-LATAM.
 *
 * La clase base game27.Keyboard se instancia en Grid con "new Keyboard()"
 * (no pasa por Builder.overrides), por lo que su placeholder del
 * autocompletado ("Start typing" / "Continue typing") queda en ingles en
 * todos los idiomas. Se sobrescribe el metodo publico hint(String) para
 * traducir unicamente esos dos textos; el resto del comportamiento es
 * identico.
 */
public class GBESLATAMKeyboard extends Keyboard {

   public GBESLATAMKeyboard() {
      super();
   }

   @Override
   public void hint(String hint) {
      if ("Start typing".equals(hint)) {
         hint = "Empieza a escribir";
      } else if ("Continue typing".equals(hint)) {
         hint = "Sigue escribiendo";
      }
      super.hint(hint);
   }
}
