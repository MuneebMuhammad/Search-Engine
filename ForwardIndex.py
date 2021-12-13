class ForwardIndexing(object):

    def __init__(self):
        self.title = {}  # stores location of each word in title
        self.content = {}   # stores location of each word in content

class Hits(object):
    def __init__(self, i, rnk, hts):
        self.docId = i
        self.rank = rnk
        self.hits = hts
