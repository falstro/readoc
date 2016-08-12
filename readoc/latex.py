from .stream import Stream
from .readoc import Document

_sections = {
    1: 'section',
    2: 'subsection',
    3: 'subsubsection',
    4: 'paragraph',
    5: 'subparagraph',
}

_headers = {
    'author': 'author',
    'authors': 'author',
    'date': 'date',
}


class Latex(Stream):
    def __init__(self, readoc, toc=False):
        super(Latex, self).__init__(readoc)
        self.__section_end = None
        self.__preamble = True
        self.__toc = toc

    def headers(self, headers):
        hs = []
        for h in headers:
            k = _headers.get(h.key.lower(), None)
            if k:
                hs.append('\\')
                hs.append(k)
                hs.append('{')
                hs.append('\n'.join(h.values))
                hs.append('}\n')

        return hs

    def title(self, text):
        return ('\\title{', text, '}\n')

    def section(self, level, numbered, text):
        if self.__preamble:
            self.__preamble = False
            r = ('\\begin{document}\n', '\\maketitle\n')
        else:
            r = ()

        if self.__section_end:
            r = self.__section_end
            self.__section_end = None

        if not numbered and level == 1:
            if text.lower() != 'abstract':
                r = r + ('\\let\\oabstractname\\abstractname',
                         '\\renewcommand{\\abstractname}{', text, '}')
            self.__section_end = (
                '\\end{abstract}\n',
                '\\renewcommand{\\abstractname}{\\oabstractname}\n',
            )
            return r + ('\\begin{abstract}\n',)

        if numbered and self.__toc:
            r = r + ('\\tableofcontents\n',)
            self.__toc = False

        return r + ('\\', _sections.get(level, '\n'),
                    '*' if not numbered else '', '{', text, '}\n')

    def para(self, begin):
        if(begin):
            pass
        else:
            return ('\n\n',)

    def unordered(self, level, lbl):
        if lbl:
            return ('\\begin{itemize}\n',)
        else:
            return ('\\end{itemize}\n',)

    def ordered(self, level, lbl):
        if lbl:
            return ('\\begin{enumerate}\n',)
        else:
            return ('\\end{enumerate}\n',)

    def item(self, text):
        return ('\\item ', text, '\n')

    def _figure(self, values):
        return (
            ('\\begin{figure}[htbp]\n',),
            ('\\caption{', ' '.join(values), '}\n', '\\end{figure}\n')
        )

    def embed(self, lead, body, trail, headers):
        t = None
        tv = None
        before = ()
        after = ()
        for h in headers:
            if h.key == 't':
                tv = h.values[0]
                t = {
                }.get(tv, None)
            elif h.key == 'Figure':
                before, after = self._figure(h.values)

        if t:
            body = t(tv, body)
        else:
            body = ('Unable...',)

        return before + body + after

    def text(self, text):
        return (text,)

    def end(self):
        return ('\\end{document}')

if __name__ == '__main__':
    import sys
    readoc = Document(sys.stdin)
    latex = Latex(readoc, toc=True)

    latex.dump(sys.stdout)
