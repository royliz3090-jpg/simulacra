# Paquete de revision de traduccion es-LATAM (SIMULACRA)

Generado por `tools/export_auditoria.py` + `tools/export_revision.py`.
**No se ha modificado el juego**: esto es solo extraccion para revision.

## Que contiene

| archivo | que es |
|---|---|
| `REVISION.jsonl` | una linea por cada texto revisable (narrativo + UI), con `en`, `es`, `owner` (recurso), `obj`, `ordinal`, `problemas` |
| `REVISION.md` | lo mismo agrupado por recurso, legible |
| `UNICOS.jsonl` | pares EN/ES **deduplicados** (una linea por texto distinto) con nº de repeticiones y problemas |
| `UNICOS.md` | version legible de `UNICOS` |
| `INDICE_RECURSOS.md` | inventario de recursos y cuantas cadenas tiene cada uno |
| `JAVA_UI.jsonl` | texto de UI incrustado en clases Java (no vive en el `.fs`) |

## Como revisar con ChatGPT

1. Empieza por `UNICOS.md`: es el conjunto minimo que cubre todo (5451 pares).
2. Los campos `problemas` marcan incidencias detectadas automaticamente:
   - `sin_traducir`: ES identico a EN.
   - `relleno_espacios`: la traduccion lleva espacios finales de relleno
     (firma de truncamiento; hay que revisar la frase).
   - `contenido_faltante`: la version ES tiene bastante menos contenido que EN
     (posible frase cortada).
   - `marcadores_distintos`: difieren los marcadores `#var#`, `__LINKn`,
     `[BOLD]`, `[]`... (NO deben perderse).
3. Pide a ChatGPT una tabla `EN -> ES_corregido` solo para las lineas marcadas.
4. Devuelve las correcciones en `en` -> `es` para aplicarlas con las herramientas
   de `tools/` (ver `docs/ESTADO_TRADUCCION.md`).

## Reglas de traduccion

- Espanol latinoamericano natural; no literal.
- Conservar SIEMPRE: variables `#state:boot.name#`, enlaces `__LINKn`,
  etiquetas `[MAIL_BOLD] ... []`, saltos de linea `\n`, prefijos
  `corrupted://`, `photoroll://`, `vo://`.
- No traducir rutas de archivo, nombres propios, codigo de triggers.

## Como se genero (reproducible)

```bash
python3 tools/export_auditoria.py --assets dist/core.assets --out exports
python3 tools/export_revision.py
python3 tools/blob_tool.py extract dist/core.binary /tmp/pycls
python3 tools/export_java_ui.py --classes /tmp/pycls --out exports/revision_chatgpt
python3 tools/validate_export.py            # comprueba cobertura 100%
```
