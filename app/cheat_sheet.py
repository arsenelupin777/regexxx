CHEAT_SHEET = r'''GUÍA LOCAL · Python 3.12 re

Funcionamiento
Coincidencias usa finditer: todas las coincidencias no superpuestas, con grupos y spans.
Se aplica al texto completo, incluidos sus saltos de línea.
MULTILINE (m) está activo por defecto: ^ y $ permiten límites de línea.
Escribe un ejemplo por línea. Con ^ y $ puedes exigir líneas completas;
sin anclas verás los fragmentos aceptados, aunque el resto de la línea sea inválido.
Los patrones que consumen saltos pueden coincidir a través de varias líneas.

Sustitución
Reemplaza todas las coincidencias con re.subn, sin cambiar Texto de prueba.
Los grupos y resaltados siguen describiendo el original, hasta 500 visibles.
El resultado incluye todas las sustituciones, también con reemplazo vacío.
\1 o \g<1>       grupo numerado: (\w+) → [\1]
\g<nombre>      grupo nombrado: (?P<nombre>\w+) → \g<nombre>!
\g<0>           coincidencia completa: \w+ → [\g<0>]
\n y \t         salto de línea y tabulación; \\ produce una barra inversa.
\g<1>0          grupo 1 seguido de 0; \10 significa grupo 10.
$1 y $nombre    texto literal, no referencias de Python.
Un reemplazo vacío elimina las coincidencias. Copiar incluye todo el resultado.
Máximo 4 000 caracteres de reemplazo y 1 000 000 en la vista previa.
El límite de vista previa se comprueba después de calcular el resultado.

Sintaxis
abc       literales; \. representa un punto literal.
.         cualquier carácter salvo \n; DOTALL incluye \n.
^ $       inicio/final; MULTILINE permite límites de línea.
\A \Z     inicio y final absolutos. $ también admite antes del salto final.
[a-z]     un carácter del rango. [^abc] excluye estos caracteres.
\d \s \w  dígito decimal, espacio, alfanumérico o _; Unicode por defecto.
\D \S \W  complementos. ASCII restringe las clases anteriores.
\b \B     límite/no límite de palabra; [\b] es un retroceso literal.
a* a+ a?  cero o más, uno o más, cero o uno.
a{2,4}    de dos a cuatro; a{2,} al menos dos; a{2} exactamente dos.
a+?       no codicioso. a++ posesivo (Python 3.11+), sin retroceso.
(a)       grupo capturado. (?:a) grupo sin captura.
(?P<x>a)  grupo nombrado; (?P=x) referencia; \1 referencia numérica.
a|b       alternativa: prueba a primero. (?>a) grupo atómico.
(?=a)     lookahead positivo; (?!a) negativo, no consumen texto.
(?<=a)    lookbehind positivo; (?<!a) negativo; ancho fijo requerido.
(?i)      flag global al inicio. (?i:a) flag local. (?#texto) comentario.
VERBOSE   ignora espacios y # comentarios fuera de clases; escapar espacios literales.

Ejemplo: (?P<usuario>\w+)@(?P<dominio>[\w.]+)
Los rangos son [inicio, fin), medidos en caracteres Python, no bytes.
Un grupo no participante devuelve None y span (-1, -1).
Un match vacío sigue siendo coincidencia: comparar con is not None.
IGNORECASE usa reglas Unicode; [A-Z] puede incluir caracteres adicionales.
Los patrones con retroceso extremo pueden agotar el tiempo del trabajador.
'''
