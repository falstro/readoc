from .stream import Stream
from .readoc import Document
from . import plugins

_graphics = ('png', 'jpg', 'svg', 'gif')


class HTML(Stream):
    def __init__(self, readoc, title='h1', subtitle='h1', sectionlevel=2):
        super(HTML, self).__init__(readoc)
        self.__level = 0
        self.__first = True

        self.__title = title
        self.__subtitle = subtitle
        self.__sectionlevel = sectionlevel

        self.__titled = False

    def title(self, text):
        if not self.__titled:
            self.__titled = True
            tag = self.__title
        else:
            tag = self.__subtitle
        begin = '<%s>' % (tag,)
        end = '</%s>' % (tag.split()[0])
        return ('%s%s%s\n' % (begin, text, end),)

    def section(self, level, numbered, text):
        level += self.__sectionlevel - 1
        if numbered:
            sections = '.'.join(str(l) for l in self.sections[:level])
            return ('\n<h%d>%s %s</h%d>\n' % (level, sections, text, level),)
        else:
            return ('\n<h%d>%s</h%d>\n' % (level, text, level),)

    def para(self, begin):
        if(begin):
            return ('<p>',)
        else:
            return ('</p>\n',)

    def unordered(self, level, lbl):
        if lbl:
            self.__level += 1
            self.__first = True
            return ('\n' if level > 1 else '',
                    '  '*(level-1), '<ul>\n')
        else:
            self.__level -= 1
            return ('</li>\n',
                    '  '*(level-1), '</ul>',
                    '\n' if level <= 1 else '')

    def ordered(self, level, lbl):
        if lbl:
            self.__level += 1
            self.__first = True
            return ('\n',
                    '  '*(level-1) + '<ol>\n')
        else:
            self.__level -= 1
            return ('</li>\n',
                    '  '*(level-1) + '</ol>',
                    '\n' if level <= 1 else '')

    def item(self, text):
        r = ('</li>\n' if not self.__first else '',
             '  '*self.__level + '<li>%s' % text)
        if self.__first:
            self.__first = False
        return r

    def _figure(self, values):
        return (
            ('<div class="figure">',),
            ('<div class="caption"><span class="label">Figure:</span> ',
             ' '.join(values), '</div></div>')
        )

    def embed(self, lead, body, trail, headers):
        before = ()
        after = ()
        plugin = plugins.embed(headers)
        for h in headers:
            if h.key.lower() == 'figure':
                before, after = self._figure(h.values)

        if plugin:
            fmt, fname = plugin(_graphics, headers, body)
            if fmt in _graphics:
                body = ('<img src="', fname, '"/>')
            else:
                body = (fname, '?')
        else:
            body = ('<pre>',) + tuple(body) + ('</pre>',)

        return before + body + after

    def text(self, text, emph):
        if text == '\n':
            return ('\n', '  '*(self.__level+2))
        return (text,)


if __name__ == '__main__':
    from . import stdio as sys
    import codecs
    readoc = Document(codecs.getreader('utf-8')(sys.stdin))
    html = HTML(readoc,
                title='h1 class="title"',
                subtitle='h1 class="subtitle"',
                sectionlevel=1)

    html.dump(codecs.getwriter('utf-8')(sys.stdout))
