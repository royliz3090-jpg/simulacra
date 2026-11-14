# SIMULACRA — Primera revisión lingüística es-LATAM

## Archivos revisados

- `PROMPT_CHATGPT.md`: instrucciones de revisión y formato de salida.
- `UNICOS.md`: 5,451 pares EN/ES y 6,226 apariciones reportadas.

## Resultado de esta pasada

- Correcciones generadas: **672** claves EN únicas, que afectan **851** apariciones en la fuente.
- Las correcciones combinan una selección de **552** casos revisados de forma contextual según el texto disponible y **120** ajustes conservadores de ortografía y puntuación.
- Validación: **0 diferencias de marcadores protegidos** detectados por la expresión de control, **0 cambios de cantidad de saltos de línea** y **0 claves de origen inventadas**.
- Algunas alertas automáticas del texto fuente no requieren cambios, por ejemplo, nombres de personajes, identificadores, fechas utilizadas por el parser y espacios finales que no significan pérdida de información.

## Ejemplos de errores resueltos

| Inglés original | Español extraído | Español propuesto |
|---|---|---|
| Justice is more important. Send the report | Si insistes. | La justicia es más importante. Envía el informe. |
| Tell me who you are | SI NO | Dime quién eres. |
| I need to lay low | Necesito | Tengo que mantener un perfil bajo. |
| Your problems, our solutions | Tus problemas, nosotros | Tus problemas, nuestras soluciones |
| Anna | Ana | Anna |

## Limitaciones y siguientes pasos

Este archivo **no acredita una revisión humana exhaustiva del 100 %** de los 5,451 pares. Quedan 2,479 registros con alertas de extracción sin resolver de forma individual, muchos por espacios de relleno o contenido protegido. Hace falta una segunda revisión contextual de las escenas y validación en el juego.

`fixes.json` es una lista **lingüística de correspondencias exactas** (`en`, `es`), no un parche binario con posiciones; no pasarlo directamente a un editor posicional ni sobrescribir `core.assets` en sitio. OpenHands debe mapear las claves `en` a todos los objetos y offsets correctos, respetar las reglas de Kryo/zlib, generar una nueva compilación y reexportar los textos para verificar los resultados. Debe revisar los casos en que el mismo inglés aparezca en distintas escenas con significados distintos.

El proyecto no se modificó desde esta sesión y no se hizo push ni se probaron los cambios dentro del juego.
