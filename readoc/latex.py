from .stream import Stream
from .readoc import Document

import hashlib
import subprocess

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
            r = ('\\begin{document}\n', '\\maketitle\n',
                 '\\let\\oabstractname\\abstractname\n')
        else:
            r = ()

        if self.__section_end:
            r = self.__section_end
            self.__section_end = None

        if not numbered and level == 1:
            if text.lower() != 'abstract':
                r = r + ('\\renewcommand{\\abstractname}{', text, '}\n')
                self.__section_end = (
                    '\\end{abstract}\n',
                    '\\renewcommand{\\abstractname}{\\oabstractname}\n',
                )
            else:
                self.__section_end = ('\\end{abstract}\n',)

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

    def _graphviz(self, cmd, lead, body, trail):
        body = ''.join(body)
        fname = hashlib.md5(body).hexdigest()
        cmd.append('-o')
        cmd.append(fname + '.eps')
        dot = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        dot.stdin.write(lead)
        dot.stdin.write(body)
        dot.stdin.write(trail)
        dot.stdin.close()
        dot.wait()

        return ('\\includegraphics{', fname, '}\n')

    def _dot(self, tv, body):
        graph = 'graph'
        for line in body:
            if '->' in line:
                graph = 'digraph'
                break
        return self._graphviz(['/usr/bin/{}'.format(tv), '-Teps'],
                              '{} x {{'.format(graph), body, '}')

    def _msc(self, tv, body):
        return self._graphviz(['/usr/bin/mscgen', '-T', 'eps'],
                              'msc {', body, '}')

    def _figure(self, values):
        return (
            ('\\begin{figure}[htbp]\n', '\\centering\n'),
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
                    'dot': self._dot,
                    'neato': self._dot,
                    'twopi': self._dot,
                    'circo': self._dot,
                    'fdp': self._dot,
                    'sfdp': self._dot,
                    'patchwork': self._dot,
                    'msc': self._msc,
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
