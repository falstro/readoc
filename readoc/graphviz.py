from .embed import filename, command, accept
from functools import partial


def dot(mode, fmts, headers, body):
    fmt = accept(
        fmts, 'eps', 'ps', 'svg', 'svgz', 'ps', 'pdf',
        'png', 'gif', 'jpg', 'jpeg'
    )

    fname = filename(mode, fmt, body)
    command(['/usr/bin/{}'.format(mode), '-T' + fmt, '-o', fname], fname, body)
    return fmt, fname


def msc(fmts, headers, body):
    fmt = accept(fmts, 'eps', 'png', 'svg', 'ismap')
    fname = filename('msc', fmt, body)
    command(['/usr/bin/mscgen', '-T' + fmt, '-o', fname], fname, body)
    return fmt, fname


EMBED = {
    v: partial(dot, v)
    for v in ('dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'patchwork')
}

EMBED['msc'] = msc
