from .embed import accept


def fileembed(fmts, headers, body):
    names = ()
    for h in headers:
        if h.key.lower() in ('file', 'filename', 'name'):
            names = h.values
            break
    else:
        names = [ln.strip() for ln in body]
    content = {name.rpartition('.')[2]: name for name in names}

    fmt = accept(fmts, *content)
    fname = content[fmt]
    return fmt, fname


EMBED = {
    "file": fileembed,
    "embed": fileembed,
}
