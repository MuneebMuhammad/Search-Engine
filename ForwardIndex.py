# Forward indexing class
class ForwardIndexing(object):

    # constructor to initialize source of publication of an article
    def __init__(self, srce):
        self.source = srce
        self.title = {}  # stores location of each word in title
        self.content = {}  # stores location of each word in content


class Hits(object):
    def __init__(self, i, rnk, hts):
        self.docId = i
        self.rank = rnk
        self.hits = hts
