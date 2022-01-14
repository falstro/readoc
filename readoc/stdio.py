import sys


def _compat(stream):
    buf = getattr(stream, 'buffer', None)
    return buf if buf else stream


stdin = _compat(sys.stdin)
stdout = _compat(sys.stdout)
