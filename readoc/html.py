from .stream import Stream
from .readoc import Readoc


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

    def text(self, text):
        return ('\n', '  '*(self.__level+2), text)


if __name__ == '__main__':
    import sys
    readoc = Readoc(sys.stdin)
    html = HTML(readoc,
                title='h1 class="title"',
                sectionlevel=1
                )

    html.dump(sys.stdout)
