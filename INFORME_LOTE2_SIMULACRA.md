# SIMULACRA — revisión lingüística, LOTE 2

## Archivos de entrada y método

- Fuente: `LOTE2.md`, 321 pares `EN` / `ES` marcados con incidencias.
- Referencia: `PROMPT_CHATGPT.md` y reglas de conservación de nombres, rutas, claves, marcadores y prefijos del juego.
- Revisión textual individual de los 321 registros y comparación con `fixes.json` (primer lote).
- Ningún archivo binario del juego ha sido modificado ni ejecutado.

## Resultado

| Concepto | Cantidad |
|---|---:|
| Registros analizados | 321 |
| Marcados `sin_traducir` por la extracción | 260 |
| Marcados `posible_truncado` | 59 |
| Marcados `contenido_faltante` | 2 |
| Nuevas correcciones propuestas | **62** |
| Registros sin modificación propuesta | **259** |
| Correcciones del primer lote | 672 |
| Correcciones acumuladas, sin duplicar claves | **734** |
| Conflictos de texto inglés con las correcciones previas | 0 |

Entre los 260 registros idénticos al inglés, la mayoría son nombres de personajes, marcas, usuarios, rutas, códigos, fechas o palabras/interjecciones que ya funcionan en español. Solo se cambiaron tres risas inglesas: `Haha`, `Hahahaha`, `Hahahahah` a sus equivalentes con `j`.

**Nota:** `sin_traducir` y `posible_truncado` son alertas heurísticas, no una confirmación de error. En el lote hay falsos positivos:

- `I am just going to look for her.` → `Voy a buscarla.` ya transmite la idea completa.
- `This service is complimentary for 1 year from this date.` → `Este servicio es gratuito por 1 año a partir de esta fecha` tiene el contenido completo (aunque no reproduce un punto final). No se propone otro cambio para evitar una edición meramente cosmética.

## Ejemplos de correcciones

| EN | ES extraído | Propuesta |
|---|---|---|
| `Already talking to other guys!??!` | `Ya esta hablando con otros` | `¿¡Ya está hablando con otros chicos!?` |
| `I saw him.. then I blacked out..` | `Lo vi.. y luego todo se puso` | `Lo vi... y luego perdí el conocimiento...` |
| `Key doesn't work?` | `La llave no` | `¿No funciona la llave?` |
| `Hi.` | `Oye` | `Hola.` |
| `Or.. maybe killed is a strong word.` | `O... tal vez matar sea una palabra` | `O... quizá «matar» sea una palabra demasiado fuerte.` |
| `What's my favourite movie?` | `Cual es mi pelicula` | `¿Cuál es mi película favorita?` |
| `pregnant!` | `preñada` | `¡Embarazada!` |

## Cadenas que requieren verificación técnica en la próxima pasada

No se han traducido automáticamente `Camera`, `Chat Images`, `Chat Audio`, `Chat Videos`, `Iris Chat`, `Me`, `Mom`, `Recovered`, `Voicemail`, `Wallpapers`, `Applesauce` ni `I R I S. OS`. Algunas pueden ser nombres de recursos, categorías, claves de búsqueda, etiquetas de álbum o textos visibles. Revisar cada aparición con su clase/recurso y uso real antes de traducirla para no provocar fallos en la lógica de SIMULACRA.

Se preservaron deliberadamente nombres de personajes, marcas, hashtags, arrobas, nombres de lugares, fechas usadas por el parser, rutas `*.web`, identificadores `__LINK...`, códigos de color y eventos/triggers del juego. Las interjecciones `Oh`, `Eh`, `Ok`, `No` y sus variantes también pueden estar correctas tal cual en un diálogo en español.

## Validaciones realizadas

- Se verificó que cada clave EN del lote corresponda a una entrada real de `LOTE2.md`.
- Se verificó que las 62 nuevas traducciones difieran de la traducción actual mostrada en el lote.
- Se preservaron los marcadores técnicos detectables por el validador y el número de saltos de línea por entrada.
- No hay conflictos entre el lote nuevo y las propuestas del primer lote por clave EN.
- Se generó un JSON válido con 62 pares nuevos y otro con 734 pares acumulados.

## Limitaciones y aplicación

Las propuestas son **correcciones lingüísticas**, no parches binarios aplicados ni pruebas del juego. OpenHands debe localizar cada coincidencia por recurso, objeto, posición y escena; resolver cualquier ambigüedad contextual de claves repetidas; aplicar los cambios en el recurso correcto; reconstruir sin corromper formatos Kryo/zlib; y reexportar los textos después de validar en el juego. Las traducciones de longitud mayor requieren el método de reconstrucción con offsets actualizados; no aplicar sustituciones ciegas de bytes in-place.

La revisión de este lote por sí sola **no certifica que todo SIMULACRA esté 100 % traducido**, porque el lote contiene solo las 321 incidencias exportadas, no todos los diálogos y escenas del videojuego.
