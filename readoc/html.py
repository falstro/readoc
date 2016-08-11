from .stream import Stream
from .readoc import Document

import subprocess
import re


class HTML(Stream):
    def __init__(self, cord, title='h1', sectionlevel=2):
        super(HTML, self).__init__(cord)
        self.__level = 0
        self.__first = True

        self.__title = title
        self.__sectionlevel = sectionlevel

    def title(self, text):
        begin = '<%s>' % (self.__title,)
        end = '</%s>' % (self.__title.split()[0])
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

    def _graphviz(self, cmd, lead, body, trail):
        dot = subprocess.Popen(cmd,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        output = ''
        error = None

        try:
            dot.stdin.write(lead)
            dot.stdin.write(''.join(body))
            dot.stdin.write(trail)
        except:
            pass
        finally:
            dot.stdin.close()

        try:
            output = dot.stdout.read()
            output = re.sub('\s*<\?.*\?>\s*', '', output)
            output = re.sub('\s*<\![^>]*>\s*', '', output)
        except:
            pass
        finally:
            dot.stdout.close()

        try:
            error = dot.stdout.read()
        except:
            pass
        finally:
            dot.stderr.close()

        if error:
            return '<pre>', error, '</pre>'

        return (output,)

    def _dot(self, tv, body):
        graph = 'graph'
        for line in body:
            if '->' in line:
                graph = 'digraph'
                break
        return self._graphviz(['/usr/bin/{}'.format(tv), '-Tsvg'],
                              '{} x {{'.format(graph), body, '}')

    def _msc(self, tv, body):
        return self._graphviz(['/usr/bin/mscgen', '-T', 'svg', '-o', '-'],
                              'msc {', body, '}')

    def _figure(self, values):
        return (
            ('<div class="figure">',),
            ('<div class="caption"><span class="label">Figure:</span> ',
             ' '.join(values), '</div></div>')
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
            body = tuple(body)

        return before + body + after

    def text(self, text):
        return ('\n', '  '*(self.__level+2), text)


if __name__ == '__main__':
    import sys
    readoc = Document(sys.stdin)
    html = HTML(readoc,
                title='h1 class="title"',
                sectionlevel=1
                )

    html.dump(sys.stdout)
