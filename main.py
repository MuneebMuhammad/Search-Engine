import json  # how to load json files
import pickle
import re
import string
import timeit
import time
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
import ForwardIndex
import os

# updates lexicon taken from Lexicon.pkl and restore the new lexicon in Lexicon.pkl
def updateLexicon(obj):
    lexicon = {}
    together = []
    punc = '''‘!()-[]{};:'"\,<>./?@#$%^&*_~'''
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    start=time.time()
    for i in range(len(obj)):
        # convert title and content to lowercase
        obj[i]['title'] = obj[i]['title'].lower()
        obj[i]['content'] = obj[i]['content'].lower()

        line = obj[i]['title']
        obj[i]['title']=""
        # remove punctuations from title and content
        for word in line.split():
            obj[i]['title']+=regex.sub('',word)
            obj[i]['title']+=" "

        line = obj[i]['content']
        obj[i]['content']=""
        for word in line.split():
            obj[i]['content']+=regex.sub('',word)
            obj[i]['content']+=" "

    print(time.time()-start)
    # words are tokinized and stemming words removed
    for i in range(len(obj)):
        together.extend([porter.stem(t) for t in word_tokenize(obj[i]['title'])])
        together.extend([porter.stem(t) for t in word_tokenize(obj[i]['content'])])
    print("done")
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

    # read json file

# for filename in os.listdir("C:/Users/rajaa/PycharmProjects/pythonProject3"):
#     if filename.endswith(".json"):
#         myjsonfile = open(filename, 'r')
#         jsondata = myjsonfile.read()
#         fileObj = json.loads(jsondata)
#         print(len(fileObj))
#         myjsonfile.close()
#         updateLexicon(fileObj)

porter = nltk.PorterStemmer()

myjsonfile = open('cbsnews.json', 'r')
jsondata = myjsonfile.read()
obj = json.loads(jsondata)
print(len(obj))
myjsonfile.close()
start = time.time()
updateLexicon(obj)

print(time.time()-start," seconds")


# for i in range(len(fileObj)):
#     line = fileObj[i]['title'].lower()
#     fileObj[i]['title']=""
#     for words in line.split():
#         fileObj[i]['title']+=words.translate(str.maketrans('','',string.punctuation))
#         fileObj[i]['title']+=" "


# line = fileObj[1]['content'].lower()
# fileObj[1]['content']=""
# regex = re.compile('[%s]' % re.escape(string.punctuation))
# for words in line.split():
#     if words=="@":
#         continue
#     fileObj[1]['content']+=regex.sub('',words)
#     fileObj[1]['content']+=" "
#
#
# print(fileObj[1]['content'])

l_file = open("Lexicon.pkl",'rb')
output = pickle.load(l_file)
#print(output)
# a_file = open("fwdix.pkl", "rb")
# previous = pickle.load(a_file)
# a_file.close()
#
# print(previous[0].content)

