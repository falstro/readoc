import re
from collections import deque

from . import tags


class Header(object):
    def __init__(self, key, left, right):
        self.key = key
        self.values = []
        self.left = left
        self.right = right

    def fit(self, left, right):
        if (self.left <= left < self.right or
                left <= self.left < right):
            self.left = min(left, self.left)
            self.right = max(left, self.right)
            return True
        return False

    def add(self, value):
        self.values.append(value)

    def __repr__(self):
        return self.key + repr(self.values)

_header_match = re.compile('([^\s:]+): *((?:\S+\s)*\S+)|'
                           '((?:\S+\s)*\S+)')
# '([^\s:]+(?:\s(?:\S+\s)*\S+)?)')


class Document(object):
    (HEAD,
     TITLE,
     LIMBO,
     PARA) = range(4)

    def __init__(self, fp):
        self.fp = fp
        self.indent = []
        self.coindent = 0
        self.state = Document.HEAD
        self.separated = False
        self.heads = []

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
        if self.state >= Document.PARA:
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

        if self.state == Document.HEAD:
            if separated:
                self.state = Document.TITLE
            else:
                for m in _header_match.finditer(line):
                    if m.group(1) is not None:
                        # new header
                        h = Header(m.group(1), m.start(1), m.end(2))
                        h.add(m.group(2))
                        self.heads.append(h)
                    else:
                        # continuation
                        for h in reversed(self.heads):
                            if(h.fit(m.start(3), m.end(3))):
                                h.add(m.group(3))
                                break
                        else:
                            # no match, assume a missing empty line.
                            self.state = Document.TITLE

                if self.state == Document.HEAD:
                    return

        i = len(line)
        line = line.lstrip()
        i -= len(line)

        o = 0

        if self.state <= Document.TITLE:
            if i > 5:
                self.q(tags.title(line))
                self.state = Document.TITLE
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
                    if self.state == Document.LIMBO:
                        self.q(tags.para(True))
                        self.state = Document.PARA
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

        if self.state < Document.LIMBO:
            self.state = Document.LIMBO

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
                if self.state == Document.PARA:
                    self.q(tags.para(False))
                    self.state = Document.LIMBO
                self.q(tags.section(level, numbered, line[o:]))
                return

        if separated and self.state == Document.PARA:
            self.q(tags.para(False))
            self.state = Document.LIMBO

        if self.state != Document.PARA:
            self.state = Document.PARA
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
