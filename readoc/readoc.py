from collections import deque

from . import tags


class Readoc(object):
    (INIT,
     TITLE,
     LIMBO,
     PARA) = range(4)

    def __init__(self, fp):
        self.fp = fp
        self.indent = []
        self.coindent = 0
        self.state = Readoc.INIT
        self.separated = False

        self._queue = deque()
        self._end = False

    def q(self, item):
        self._queue.append(item)

    def pop(self):
        while not self._queue:
            if self._end:
                return None
            line = self.fp.readline()
            if not line:
                self._end = True
                self.end()

            self.line(line)

        return self._queue.popleft()

    def __iter__(self):
        return self

    def next(self):
        n = self.pop()
        if n is None:
            raise StopIteration()
        return n

    def _clean_para(self):
        if self.state >= Readoc.PARA:
            self.q(tags.para(False))

    def _clean_lists(self):
        for lvl, (xi, xt) in enumerate(self.indent):
            self.q(xt(len(self.indent) - lvl, None))
        del self.indent[:]

    def end(self):
        self._clean_lists()
        self._clean_para()
        self.q(tags.end())

    def line(self, line):
        line = line.rstrip().expandtabs()
        # import sys
        # sys.stderr.write('\n>>> %s\n' % line)

        if not line:
            self.separated = True
            return

        separated = self.separated
        self.separated = False

        i = len(line)
        line = line.lstrip()
        i -= len(line)

        o = 0

        if self.state <= Readoc.TITLE:
            if i > 5:
                self.q(tags.title(line))
                self.state = Readoc.TITLE
                return

        if i > 0:
            tag = None
            lbl, o = self.ordered(line)
            if lbl:
                tag = tags.ordered
            else:
                lbl, o = self.unordered(line)
                if lbl:
                    tag = tags.unordered

            if tag:
                xi, xt = -1, None
                while self.indent:
                    xi, xt = self.indent[-1]
                    if i < xi:
                        self.q(xt(len(self.indent), None))
                        self.indent.pop()
                    else:
                        break
                else:
                    xi, xt = -1, None

                if i == xi and not xt == tag:
                    self.q(xt(len(self.indent), None))
                    self.indent.pop()
                    self.indent.append((i, tag))
                    self.q(tag(len(self.indent), lbl))
                elif i > xi:
                    if self.state == Readoc.LIMBO:
                        self.q(tags.para(True))
                        self.state = Readoc.PARA
                    self.indent.append((i, tag))
                    self.q(tag(len(self.indent), lbl))

                self.q(tags.item(line[o:]))
                self.coindent = o
                return

            if i >= self.coindent:
                self.q(tags.text(line[o:]))
                return

        # We're looking at body text or possibly a section heading,
        # clear out running lists.
        self._clean_lists()

        if i == 0 and line:
            level = 0
            numbered = True
            while True:
                num, o = self.num(line, o)
                if num is None:
                    break
                if not (level or int(num)):
                    numbered = False

                level += 1

                if line[o] == '.':
                    o += 1
                elif line[o].isspace():
                    break

            if level:
                o = self._skip(line, o)
                if self.state == Readoc.PARA:
                    self.q(tags.para(False))
                    self.state = Readoc.LIMBO
                self.q(tags.section(level, numbered, line[o:]))
                return

        if separated and self.state == Readoc.PARA:
            self.q(tags.para(False))
            self.state = Readoc.LIMBO

        if self.state != Readoc.PARA:
            self.state = Readoc.PARA
            self.q(tags.para(True))

        self.q(tags.text(line))

    def num(self, line, o):
        b = o
        while '0' <= line[o] <= '9':
            o += 1

        return (line[b:o] if o > b else None, o)

    def _skip(self, line, o):
        for x in line[o:]:
            if not x.isspace():
                break
            o += 1
        return o

    def _check_set(self, line, o, args):
        c = 0
        for x in line[o+1:]:
            if x in args:
                c += 1
        return c

    def ordered(self, line, o=0):
        for roman in (('i', 'v', 'x'), ('I', 'V', 'X')):
            c = self._check_set(line, o, roman)
            if c and line[o+c] == '.':
                return line[o:o+c], self._skip(line, o+c+1)

        if line[o].isalpha() and line[o+1] == '.':
            return line[o], self._skip(line, o+2)

        n, o = self.num(line, o)
        if n is not None and line[o] == '.':
            return n, self._skip(line, o+1)

        return None, o

    def unordered(self, line, o=0):
        if line[o] in ('-', '+', '*') and line[o+1].isspace():
            return line[o], self._skip(line, o+2)
        return None, o
