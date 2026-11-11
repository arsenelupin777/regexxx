# Regexxx

Una app de escritorio sencilla para probar expresiones regulares, encontrar coincidencias y experimentar con reemplazos. Hecha con **Python + PyQt6**, con interfaz en español y el motor `re` de Python.

## ¿Qué puedes hacer?

- Ver las coincidencias resaltadas mientras escribes.
- Explorar grupos de captura y sus posiciones en el texto.
- Probar sustituciones y copiar el resultado.
- Activar opciones como ignorar mayúsculas (`i`) o trabajar con varias líneas (`m`).
- Cambiar entre tema claro y oscuro.
- Consultar una guía rápida integrada con el botón **?**.

## Pruébalo

Escribe este patrón en el campo de expresión regular:

```regex
\b\d+\b
```

Y pega este texto en **Texto de prueba**:

```text
"Tengo 2 ladrillos en las manos y tengo 4 cafeteras en mi casa" -Momo Benavides
```

Se resaltarán `2` y `4`. Luego cambia a **Sustitución**, escribe `#` como reemplazo y verás:

```text
"Tengo # ladrillos en las manos y tengo # cafeteras en mi casa" -Momo Benavides
```

## Algunos detalles

- Escribe los patrones directamente, sin envolverlos en `/.../`.
- Usa **F3** y **Shift + F3** para recorrer las coincidencias.
- La opción multilínea (`m`) está activada por defecto.
- El texto se procesa localmente en tu equipo.
- Se muestran hasta **500 coincidencias**, con un máximo de **100 000 caracteres de texto** y **4 000 de patrón**. Las evaluaciones se interrumpen tras **2 segundos** para evitar bloqueos.

---

Hecho para practicar, experimentar y compartir entre panitas. 🙂
