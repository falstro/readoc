import textwrap
from math import floor

from .stream import Stream
from .readoc import Document

from itertools import chain
from dataclasses import dataclass
import typing as T


@dataclass
class ItemGenerator:
    generator: T.Generator[str, None, None]
    lead: str = ''


class Normalize(Stream):
    def __numeric(self, i=1):
        while True:
            yield str(i) + '. '
            i += 1

    def __bullet(self, b='-'):
        b += ' '
        while True:
            yield b

    def __init__(self, readoc, justify=False, width=78, section_trail=False):
        super(Normalize, self).__init__(readoc)

        self.__text = []
        self.__lists = []
        self.__level = 0
        self.__width = width
        self.__section_trail = section_trail
        self.__wrapper = textwrap.TextWrapper()
        self.__reset()

        if justify is True:
            self.__align = self.__justify
        elif justify is False:
            self.__align = self.__packjustify
        else:
            self.__align = self.__nojustify

    def __packjustify(self, line, left, right):
        # TODO Be wary of markup containing spaces.
        words = line[left:].split()
        return line[:left] + ' '.join(words)

    def __justify(self, line, left, right):
        # TODO Be wary of markup containing spaces.

        words = line[left:].split()
        fill = right - left - (sum(len(x) for x in words)) - (len(words) - 1)
        if fill <= 0:
            return line

        last = words.pop()
        df = fill/float(len(words))
        tf = 0
        for i, word in enumerate(words):
            tf += df
            if tf >= 1:
                words[i] = word + ' '*int(floor(tf))
                tf -= floor(tf)

        if tf > 0.5:
            last = ' '+last
        words.append(last)
        return line[:left] + ' '.join(words)

    def __nojustify(self, line, left, right):
        return line

    def __flush(self):
        if not self.__text:
            return ()
        wrapped = self.__wrapper.wrap(' '.join(self.__text))
        left = len(self.__wrapper.initial_indent)
        right = self.__width
        last = wrapped.pop()
        r = tuple(self.__align(w, left, right) + '\n' for w in wrapped)
        del self.__text[:]
        return r + (last, '\n')

    def __reset(self):
        self.__wrapper.initial_indent = '  '
        self.__wrapper.subsequent_indent = '  '
        self.__wrapper.width = self.__width

    def _center(self, text, minindent=0):
        indent = (self.__width-len(text))//2
        if indent < minindent:
            indent = minindent
        return (' '*indent, text)

    def title(self, text):
        return self.__flush() + self._center(text, 5) + ('\n'*3,)

    def section(self, level, numbered, text):
        if numbered:
            sections = self.sections[:level]
        else:
            sections = [0] + self.sections[1:level]

        sections = '.'.join(str(lbl) for lbl in sections)
        if self.__section_trail:
            sections += '.'
        return self.__flush() + ('%s %s\n\n' % (sections, text),)

    def para(self, begin):
        if(begin):
            return self.__flush()
        else:
            return self.__flush() + ('\n',)

    def unordered(self, level, lbl):
        r = self.__flush()
        if lbl:
            self.__lists.append(ItemGenerator(self.__bullet()))
            self.__level += 1
        else:
            self.__lists.pop()
            self.__level -= 1
            self.__item_continue()
            if not self.__lists:
                self.__reset()
        return r

    def ordered(self, level, lbl):
        r = self.__flush()
        if lbl:
            if lbl.isdigit():
                gen = self.__numeric(int(lbl))
            else:
                gen = self.__numeric()
            self.__lists.append(ItemGenerator(gen))
            self.__level += 1
        else:
            self.__lists.pop()
            self.__level -= 1
            self.__item_continue()
            if not self.__lists:
                self.__reset()
        return r

    def __item_continue(self):
        if self.__lists:
            self.__wrapper.subsequent_indent = self.__lists[-1].lead
            self.__wrapper.initial_indent = self.__wrapper.subsequent_indent

    def item(self, text):
        r = self.__flush()
        itgen = self.__lists[-1]
        b = next(itgen.generator)
        ind = '  '*(self.__level+1)

        itgen.lead = ind + ' '*len(b)
        self.__wrapper.initial_indent = ind + b
        self.__wrapper.subsequent_indent = itgen.lead
        self.__wrapper.width = self.__width
        self.__text.append(text)
        return r

    def text(self, text, emph):
        text = text.strip()
        if text:
            if emph:
                self.__text.append('*%s*' % (text,))
            else:
                self.__text.append(text)
        return ()

    def embed(self, lead, body, trail, headers):
        return chain(
            self.__flush(),
            self._center(lead.strip()),
            ('\n',),
            body,
            self._center(trail.strip()),
            ('\n',)
        )

    def end(self):
        return self.__flush()


if __name__ == '__main__':
    from . import stdio as sys
    import codecs
    readoc = Document(codecs.getreader('utf-8')(sys.stdin))
    normalize = Normalize(readoc, justify=None)

    normalize.dump(codecs.getwriter('utf-8')(sys.stdout))
