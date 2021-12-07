class ForwardIndexing(object):

    # constructor to initialize source and author of publication of an article
    def __init__(self, srce, athr):
        self.source = srce
        self.author = athr
        self.title = {}  # stores location of each word in title
        self.content = {}   # stores location of each word in content

