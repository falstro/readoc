from .stream import Stream
from .readoc import Document
from . import plugins

from itertools import chain

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

_graphics = ('pdf', 'eps', 'png')


class Latex(Stream):
    def __init__(self, readoc, toc=False, def_headers=False):
        super(Latex, self).__init__(readoc)
        self.__section_end = None
        self.__preamble = True
        self.__toc = toc
        self.__def_headers = def_headers

        self.__titled = None

    def _sanitize(self, text):
        # TODO sanitize text (i.e. escape latex control characters)
        return text.strip()

    def _sanitize_all(self, values):
        return (self._sanitize(v) for v in values)

    def headers(self, headers):
        hs = ['\\makeatletter']
        for h in headers:
            k = _headers.get(h.key.lower(), None)
            if k:
                hs.append('\\')
                hs.append(k)
                hs.append('{')
                hs.append('\n'.join(self._sanitize_all(h.values)))
                hs.append('}\n')
            elif self.__def_headers:
                hs.append('\\def\\')
                hs.append(self.__def_headers)
                hs.append(h.key)
                hs.append('{')
                hs.append('\n'.join(self._sanitize_all(h.values)))
                hs.append('}\n')

        hs.append('\\makeatother')
        return hs

    def title(self, text):
        if not self.__titled:
            self.__titled = self._sanitize(text)
            return (
                '\\makeatletter\\def\\@maintitle{', self.__titled, '}',
                '\\title{', self.__titled, '}\n'
            )
        else:
            self.__titled = self.__titled \
                + '\\\\[7pt] \\large ' + self._sanitize(text)
        return ('\\title{', self.__titled, '}\n')

        # if self.__titled:
        #     return ('\\renewcommand\\subtitle{', self._sanitize(text), '}\n')
        # self.__titled = True
        # return ('\\newcommand\\subtitle{}\n',
        #         '\\title{', self._sanitize(text), '\\subtitle}\n')

    def section(self, level, numbered, text):
        if self.__preamble:
            self.__preamble = False
            r = ('\\begin{document}\n', '\\maketitle\n',
                 '\\let\\oabstractname\\abstractname\n')
        elif self.__section_end:
            r = self.__section_end
            self.__section_end = None
        else:
            r = ()

        if not numbered and level == 1:
            if text.lower() != 'abstract':
                r = chain(r, ('\\renewcommand{\\abstractname}{', text, '}\n'))
                self.__section_end = (
                    '\\end{abstract}\n',
                    '\\renewcommand{\\abstractname}{\\oabstractname}\n',
                )
            else:
                self.__section_end = ('\\end{abstract}\n',)

            return chain(r, ('\\begin{abstract}\n',))

        if numbered and self.__toc:
            r = chain(r, ('\\tableofcontents\n',))
            self.__toc = False

        return chain(r, ('\\', _sections.get(level, '\n'),
                         '*' if not numbered else '',
                         '{', self._sanitize(text), '}\n'))

    def para(self, begin):
        if(begin):
            pass
        else:
            return ('\n\n',)

    def itembreak(self):
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
        return ('\\item ', self._sanitize(text), '\n')

    def _figure(self, values):
        return (
            ('\\begin{figure}[htbp]\n', '\\centering\n'),
            ('\\caption{', ' '.join(self._sanitize_all(values)), '}\n',
             '\\end{figure}\n')
        )

    def _listing(self, values):
        return (
            ('\\begin{lstlisting}[caption=',
             ' '.join(self._sanitize_all(values)), ']\n'),
            ('\\end{lstlisting}\n')
        )

    def embed(self, lead, body, trail, headers):
        before = ()
        after = ()
        plugin = plugins.embed(headers)
        verbatim = True
        opts = []
        for h in headers:
            if h.key.lower() == 'figure':
                before, after = self._figure(h.values)
            elif h.key.lower() == 'listing':
                before, after = self._listing(h.values)
                verbatim = False
            elif h.key.lower() == 'width':
                opts.append('width=' + ' '.join(h.values))
            elif h.key.lower() == 'height':
                opts.append('height=' + ' '.join(h.values))
            elif h.key.lower() == 'scale':
                opts.append('scale=' + ' '.join(h.values))

        if plugin:
            fmt, fname = plugin(_graphics, headers, body)
            if fmt in _graphics:
                body = ('\\centerline{\\includegraphics[',
                        ', '.join(opts),
                        ']{', fname, '}}\n')
            else:
                body = (fname, '?\n')
        elif verbatim:
            body = ('\\begin{verbatim}' + ''.join(body) + '\\end{verbatim}',)

        return chain(before, body, after)

    def text(self, text, emph):
        txt = self._sanitize(text)
        if not txt:
            return ()
        if emph:
            return ('\\emph{', txt, '}', '\n')
        return (txt, '\n')

    def end(self):
        return ('\\end{document}',)


if __name__ == '__main__':
    from . import stdio as sys
    import codecs
    readoc = Document(codecs.getreader('utf-8')(sys.stdin))
    latex = Latex(readoc, toc=True, def_headers='readoc@')

    latex.dump(codecs.getwriter('utf-8')(sys.stdout))
