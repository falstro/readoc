from .embed import filename, accept

from base64 import b64decode

import os.path


def base64(fmts, headers, body):
    content = ()
    for h in headers:
        if h.key.lower() == 'format':
            content = h.values
            break

    fmt = accept(fmts, *content)
    fname = filename('base64', fmt, body)
    if not os.path.exists(fname):
        with open(fname, 'wb') as fp:
            for part in body:
                fp.write(b64decode(part))

    return fmt, fname


EMBED = {
    "base64": base64,
    "b64": base64
}
