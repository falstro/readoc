from . import graphviz, plantuml, b64embed

from itertools import chain

EMBED = dict(
    chain.from_iterable(m.EMBED.items() for m in
                        (graphviz, plantuml, b64embed))
)


class Plugged(object):
    def __init__(self, embed):
        self.embed = embed

    def __call__(self, fmts, headers, body):
        return self.embed(fmts, headers, body)


def rchop(s, sub):
    return s[:-len(sub)] if sub and s.endswith(sub) else s


def embed(headers):
    for h in headers:
        if h.key in ('\\_', '|'):
            trailer = {'\\_': ':_/', '|': ':|'}
            plugin = EMBED.get(rchop(h.values[0], trailer.get(h.key)))
            if not plugin:
                return None
            return Plugged(plugin)
