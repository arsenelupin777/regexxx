"""Pure Python engine. The GUI calls this only in an isolated process."""
import re
from functools import lru_cache
from itertools import islice
from typing import Any

MAX_MATCHES = 500
MAX_TEXT = 100_000
MAX_PATTERN = 4_000
MAX_REPLACEMENT = 4_000
MAX_PREVIEW = 1_000_000


@lru_cache(maxsize=32)
def compile_pattern(pattern: str, flags: int) -> re.Pattern[str]:
    return re.compile(pattern, flags)


def evaluate(pattern: str, text: str, flags: int = 0,
             operation: str = 'match', replacement: str = '') -> dict[str, Any]:
    if len(text) > MAX_TEXT or len(pattern) > MAX_PATTERN:
        return {'state': 'limit', 'error': 'Límite: 100 000 caracteres de texto y 4 000 de patrón.', 'position': None}
    try:
        regex = compile_pattern(pattern, flags)
        matches = list(islice(regex.finditer(text), MAX_MATCHES + 1))
        result = {'state': 'matches' if matches else 'no_match', 'matches': [
            {'text': m.group(), 'span': m.span(), 'groups': [
                {'number': n, 'name': next((name for name, index in regex.groupindex.items()
                                          if index == n), None),
                 'text': m.group(n), 'span': m.span(n)}
                for n in range(1, regex.groups + 1)]}
            for m in matches[:MAX_MATCHES]], 'truncated': len(matches) > MAX_MATCHES}
    except (re.error, ValueError, OverflowError, IndexError, RecursionError) as error:
        return {'state': 'invalid', 'error': 'Patrón: ' + str(error), 'error_source': 'pattern', 'position': getattr(error, 'pos', None),
                'line': getattr(error, 'lineno', None), 'column': getattr(error, 'colno', None)}
    if operation == 'substitution':
        result.update(output=None, substitution_count=None)
        if len(replacement) > MAX_REPLACEMENT:
            result.update(state='limit', error='Reemplazo: límite de 4 000 caracteres.',
                          error_source='replacement', position=None)
            return result
        try:
            output, count = regex.subn(replacement, text)
        except (re.error, ValueError, OverflowError, IndexError, RecursionError) as error:
            result.update(state='invalid', error='Reemplazo: ' + str(error),
                          error_source='replacement', position=getattr(error, 'pos', None),
                          line=getattr(error, 'lineno', None), column=getattr(error, 'colno', None))
            return result
        result['substitution_count'] = count
        # This is a display limit, checked after subn allocates the full result.
        if len(output) > MAX_PREVIEW:
            result.update(state='limit', error=f'{count} sustituciones · El resultado supera 1 000 000 de caracteres; vista previa no disponible.',
                          position=None)
        else:
            result['output'] = output
    return result

