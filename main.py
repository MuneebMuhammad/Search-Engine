import json  # how to load json files
import pickle
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
import ForwardIndex


# updates lexicon taken from Lexicon.pkl and restore the new lexicon in Lexicon.pkl
def updateLexicon(obj):
    lexicon = {}
    together = []
    punc = '''‘!()-[]{};:'"\,<>./?@#$%^&*_~'''

    for i in range(len(obj)):
        # convert title and content to lowercase
        obj[i]['title'] = obj[i]['title'].lower()
        obj[i]['content'] = obj[i]['content'].lower()

        # remove punctuations from title and content
        for l in obj[i]['title']:
            if l in punc[4]:
                obj[i]['title'] = obj[i]['title'].replace(l, ' ')
            elif l in punc:
                obj[i]['title'] = obj[i]['title'].replace(l, '')
        for l in obj[i]['content']:
            if l in punc[4]:
                obj[i]['content'] = obj[i]['content'].replace(l, ' ')
            elif l in punc:
                obj[i]['content'] = obj[i]['content'].replace(l, '')
        # words are tokinized and stemming words removed
        together.extend([porter.stem(t) for t in word_tokenize(obj[i]['title'])])
        together.extend([porter.stem(t) for t in word_tokenize(obj[i]['content'])])
    # remove duplicates
    together = set(together)

    # remove stopwords
    together = [word for word in together if not word in stopwords.words('english')]
    together = [word for word in together if not word.isdigit()]
    # add words and word_ID to lexicon
    for ii, wdd in enumerate(together):
        lexicon[wdd] = ii

    # create file if it don't exists and add Lexicon to the file
    if not Path('Lexicon.pkl').is_file():
        a_file = open("Lexicon.pkl", "wb")
        pickle.dump(lexicon, a_file)
        a_file.close()
    # if file already exists then add unique elements of new lexicon to new lexicon
    else:
        a_file = open("Lexicon.pkl", "rb")
        previous = pickle.load(a_file)
        a_file.close()
        for keywd, valID in lexicon.items():
            if keywd not in previous:
                previous[keywd] = valID
        a_file = open("Lexicon.pkl", "wb")
        pickle.dump(previous, a_file)
        a_file.close()
    forwardI(obj)


# builds forward indexing
def forwardI(obj):
    # read lexicon
    a_file = open("Lexicon.pkl", "rb")
    lexicon = pickle.load(a_file)
    a_file.close()

    docs = []  # docs will store each article's detail
    n = len(obj)
    for i in range(n):
        docs.append(ForwardIndex.ForwardIndexing(obj[i]['source'],
                                                 obj[i]['author']))  # append author and source of the article to docs

        # store words and their locations in an article's title
        tltk = [porter.stem(t) for t in word_tokenize(obj[i]['title'])]
        for loc, wd in enumerate(tltk):
            if wd in lexicon:
                wids = lexicon[wd]
                if wids not in docs[i].title:
                    docs[i].title[wids] = []
                docs[i].title[wids].append(loc)

        # store words and their locations in an article's content
        wdtk = word_tokenize(obj[i]['content'])
        for loc, wd in enumerate(wdtk):
            if wd in lexicon:
                wids = lexicon[wd]
                if wids not in docs[i].content:
                    docs[i].content[wids] = []
                docs[i].content[wids].append(loc)

    # if forward indexing file don't exist then create it and add the article details to it
    if not Path('fwdix.pkl').is_file():
        a_file = open("fwdix.pkl", "wb")
        pickle.dump(docs, a_file)
        a_file.close()
    # if file already exists then append new article details to previous ones
    else:
        a_file = open("fwdix.pkl", "rb")
        previous = pickle.load(a_file)
        a_file.close()
        previous.extend(docs)
        a_file = open("fwdix.pkl", "wb")
        pickle.dump(previous, a_file)
        a_file.close()

    # read json file


myjsonfile = open('21stcenturywire.json', 'r')
jsondata = myjsonfile.read()
fileObj = json.loads(jsondata)
myjsonfile.close()

porter = nltk.PorterStemmer()

updateLexicon(fileObj)

# checking results of forward indexing
a_file = open("fwdix.pkl", "rb")
previous = pickle.load(a_file)
a_file.close()

print(previous[0].title)

