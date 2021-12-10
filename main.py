import json  # how to load json files
import pickle
import re
import time
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
import ForwardIndex
from nltk.stem.snowball import SnowballStemmer


# updates lexicon taken from Lexicon.pkl and restore the new lexicon in Lexicon.pkl
def updateLexicon(obj):
    lexicon = {}
    together = []

    # compile the regex so every character that is not a word or a space will be removed
    regex = re.compile(r"[^\w\s]")

    start = time.time()
    for i in range(len(obj)):
        # convert title and content to lowercase
        obj[i]['title'] = obj[i]['title'].lower()
        obj[i]['content'] = obj[i]['content'].lower()

        # get the title in the line variable and apply regex
        line = obj[i]['title']
        obj[i]['title'] = ""
        line = regex.sub(' ', line)
        # remove punctuations from title and content
        # re-intialize the title word by word from line
        for word in line.split():
            if not word.isdigit():
                obj[i]['title'] += word
                obj[i]['title'] += " "

        # get the content in the line variable and apply regex
        line = obj[i]['content']
        obj[i]['content'] = ""
        line = regex.sub(' ', line)
        # remove punctuations from title and content
        # re-intialize the content word by word from line
        for word in line.split():
            if not word.isdigit():
                obj[i]['content'] += word
                obj[i]['content'] += " "

        # words are tokenized and stemming removed
        together.extend([snow_stemmer.stem(t) for t in word_tokenize(obj[i]['title'])])
        together.extend([snow_stemmer.stem(t) for t in word_tokenize(obj[i]['content'])])

    # remove duplicates
    together = set(together)
    # remove stopwords
    together = [word for word in together if not word in stopwords.words('english')]

    print(time.time() - start)
    print("done")
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
    s = time.time()
    a_file = open("Lexicon.pkl", "rb")
    lexicon = pickle.load(a_file)
    a_file.close()
    print(time.time() - s)
    docs = []  # docs will store each article's detail
    n = len(obj)
    for i in range(n):
        docs.append(ForwardIndex.ForwardIndexing(obj[i]['source'],
                                                 obj[i]['author']))  # append author and source of the article to docs

        # store words and their locations in an article's title
        tltk = word_tokenize(obj[i]['title'])
        for loc, wd in enumerate(tltk):
            wd = snow_stemmer.stem(wd)
            if wd in lexicon:
                wids = lexicon[wd]
                if wids not in docs[i].title:
                    docs[i].title[wids] = []
                docs[i].title[wids].append(loc)

        # store words and their locations in an article's content
        wdtk = word_tokenize(obj[i]['content'])
        for loc, wd in enumerate(wdtk):
            wd = snow_stemmer.stem(wd)
            if wd in lexicon:
                wids = lexicon[wd]
                if wids not in docs[i].content:  # changed
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
    createInvertedIndex()


def createInvertedIndex():
    # load the lexicon
    a_file = open("Lexicon.pkl", "rb")
    lexicon = pickle.load(a_file)
    a_file.close()

    # load the forward index
    a_file = open("fwdix.pkl", 'rb')
    fwdIdx = pickle.load(a_file)
    a_file.close()

    # dict to store inverted index
    invertedIndex = {}

    for wd in lexicon:
        wid = lexicon[wd]
        # if word is not in the inverted idex create an empty list for it
        if wid not in invertedIndex:
            invertedIndex[wid] = []
        for i in range(len(fwdIdx)):
            rank = 0
            hits = 0
            # flag indicates if a word has been found in a particular document
            flag = False
            # if the word in title calculate hits and rank
            if wid in fwdIdx[i].title:
                hits += len(fwdIdx[i].title[wid])
                rank += hits * 5
                flag = True
            # if the word in content calculate hits and rank
            if wid in fwdIdx[i].content:
                hits += len(fwdIdx[i].content[wid])
                rank += hits * 3
                flag = True
            # if the word in author calculate hits and rank
            if wid == fwdIdx[i].author:
                hits += 1
                rank += 150
                flag = True
            # if the word in source calculate hits and rank
            if wid == fwdIdx[i].source:
                hits += 1
                rank += 100
                flag = True
            if flag:
                # if flag is true append the docId, rank and hits for that word
                invertedIndex[wid].append(ForwardIndex.Hits(i, rank, hits))
            flag = False
    # create file if it don't exists and add invertedIndex to the file
    if not Path('InvertedIndex.pkl').is_file():
        a_file = open("InvertedIndex.pkl", "wb")
        pickle.dump(invertedIndex, a_file)
        a_file.close()
    # if file already exists then add unique elements of new invertedIndex
    else:
        a_file = open("InvertedIndex.pkl", "rb")
        previous = pickle.load(a_file)
        a_file.close()
        previous.extend(invertedIndex)
        a_file = open("InvertedIndex.pkl", "wb")
        pickle.dump(previous, a_file)
        a_file.close()


snow_stemmer = SnowballStemmer(language='english')

myjsonfile = open('21stcenturywire.json', 'r')
jsondata = myjsonfile.read()
obj = json.loads(jsondata)
myjsonfile.close()

updateLexicon(obj)

l_file = open("Lexicon.pkl", 'rb')
output = pickle.load(l_file)
print(output)

# f_file = open("fwdix.pkl", "rb")
# fwdIndx = pickle.load(f_file)
# f_file.close()
#
# i_file = open("InvertedIndex.pkl", "rb")
# invtdIndx = pickle.load(i_file)
# i_file.close()
#
# print(fwdIndx[139].content)
# print(invtdIndx[5538][1].rank)
