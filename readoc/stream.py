import sys

from . import tags


class Stream(object):
    def __init__(self, cord):
        self.cord = cord

        self.map = {
            tags.title: self._title,
            tags.section: self._section,
            tags.para: self._para,

            tags.ordered: self._ordered,
            tags.unordered: self._unordered,
            tags.item: self._item,

            tags.text: self._text,

            tags.end: self._end
        }
        self.sections = []

    def dump(self, out):
        for e in self.cord:
            fn = self.map.get(e[0], None)
            if fn:
                text = fn(*e[1:])
                if text:
                    out.write(''.join(text))
            else:
                self.unknown(e)
        self.end()

    def _title(self, text):
        return self.title(text)

    def title(self, text):
        return ()

    def _section(self, level, numbered, text):
        if level > len(self.sections):
            new = level - len(self.sections)
            self.sections.extend(0 for _ in range(new))
        elif level < len(self.sections):
            del self.sections[level:]

        if level > 1 or numbered:
            self.sections[level-1] += 1

        return self.section(level, numbered, text)

    def section(self, level, numbered, text):
        return ()

    def _end(self):
        return self.end()

    def end(self):
        return ()

    def _para(self, begin):
        return self.para(begin)

    def para(self, begin):
        return ()

    def _ordered(self, level, lbl):
        return self.ordered(level, lbl)

    def ordered(self, level, lbl):
        return ()

    def _unordered(self, level, lbl):
        return self.unordered(level, lbl)

    def unordered(self, level, lbl):
        return ()

    def _item(self, text):
        return self.item(text)

    def item(self, text):
        return ()

    def _text(self, text):
        return self.text(text)

    def text(self, text):
        return ()

    def unknown(self, args):
        sys.stderr.write('Unknown tag %s\n' % (repr(args)))
