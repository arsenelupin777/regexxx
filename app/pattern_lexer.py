import re

def tokens(text, flags=0):
    result, stack = [], []
    verbose = bool(flags & re.X)
    i = 0
    while i < len(text):
        start, kind = i, None
        c = text[i]
        if c == '\\':
            i = min(i+2, len(text)); kind = 'escape'
        elif verbose and c == '#':
            end = text.find('\n', i)
            i = len(text) if end < 0 else end; kind = 'comment'
        elif text.startswith('(?#', i):
            end = text.find(')', i+3)
            i = len(text) if end < 0 else end+1; kind = 'comment'
        elif c == '[':
            i += 1
            if i < len(text) and text[i] == '^': i += 1
            if i < len(text) and text[i] == ']': i += 1
            while i < len(text):
                if text[i] == '\\': i = min(i+2, len(text))
                elif text[i] == ']':
                    i += 1; kind = 'class'; break
                else: i += 1
        elif c == '(':
            inline = re.match(r'\(\?([aiLmsux]*)(?:-([imsx]+))?([:)])', text[i:])
            if inline:
                added, removed, ending = inline.groups()
                if ending == ':': stack.append(verbose)
                verbose = (verbose or 'x' in added) and 'x' not in (removed or '')
                i += len(inline.group())
            else:
                stack.append(verbose); i += 1
            kind = 'group'
        elif c == ')':
            if stack: verbose = stack.pop()
            i += 1; kind = 'group'
        elif c == '{':
            quantifier = re.match(r'\{(?:\d+|\d*,\d*)\}[?+]?', text[i:])
            i += len(quantifier.group()) if quantifier else 1
            kind = 'repeat' if quantifier else None
        else:
            i += 1
            kind = 'repeat' if c in '*+?' else 'anchor' if c in '^$.' else 'group' if c == '|' else None
        if kind: result.append((start, i, kind))
    return result
