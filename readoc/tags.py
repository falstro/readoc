class Tag(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        return (self,) + args

    def __repr__(self):
        return self.name

headers = Tag('headers')

title = Tag('title')
section = Tag('section')
para = Tag('para')

ordered = Tag('ordered')
unordered = Tag('unordered')
item = Tag('item')
itembreak = Tag('itembreak')

text = Tag('text')

embed = Tag('embed')

end = Tag('end')
