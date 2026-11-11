"""Local reusable worker; newline-delimited JSON over anonymous pipes."""
import json
import sys
from app.regex_engine import evaluate


def main():
    for line in sys.stdin.buffer:
        request = json.loads(line)
        result = evaluate(**request['input'])
        sys.stdout.buffer.write((json.dumps(dict(revision=request['revision'], result=result),
                                           ensure_ascii=True) + '\n').encode('ascii'))
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
