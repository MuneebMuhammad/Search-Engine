import json  # how to load json files
import pickle
import re
import os
import time
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
import ForwardIndex
from nltk.stem.snowball import SnowballStemmer
import time
import string


def updateLexicon(obj):
    # parse through every article in each document
    for i in range(len(obj)):
        # add author and source of article to forward index title
        srce = obj[i]['source'].lower()
        srce = snow_stemmer.stem(srce)
        if srce not in lexicon:
            lexicon[srce] = lexicon[(list(lexicon)[-1])] + 1
        athr = obj[i]['author'].lower()
        athr = snow_stemmer.stem(athr)
        if athr not in lexicon:
            lexicon[athr] = lexicon[(list(lexicon)[-1])] + 1
        docs.append(ForwardIndex.ForwardIndexing())
        docs[-1].title[lexicon[athr]] = [0]
        docs[-1].title[lexicon[srce]] = [1]

        # parse through each character in title and collect alphabetical words with size greater than 3
        t = obj[i]['title']
        word = ""
        loc = 2
        for char in t:
            # append characters is character is alphabet
            if char.isalpha():
                word += char
            else:
                # if word size is less than 3 then discharge the word and start with new word
                if len(word) <= 3:
                    word = ""
                    continue
                word = word.lower()  # convert word to lower case
                word = snow_stemmer.stem(word)  # perform stemming on the word
                # if word is not in lexicon then add the word to lexicon with 'word id = word_id of last element in dictionary + 1'
                if word not in lexicon:
                    lexicon[word] = lexicon[(list(lexicon)[-1])] + 1
                wid = lexicon[word]
                # add the word along with its location if the word exists in title
                if wid not in docs[-1].title:
                    docs[-1].title[wid] = []
                docs[-1].title[wid].append(loc)
                loc += 1
                word = ""

        # perform the same operation with content data of the article
        c = obj[i]['content']
        word = ""
        loc = 0
        for char in c:
            if char.isalpha():
                word += char
            else:
                if len(word) <= 3:
                    word = ""
                    continue
                word = word.lower()

                word = snow_stemmer.stem(word)
                if word not in lexicon:
                    lexicon[word] = lexicon[list(lexicon)[-1]] + 1
                wid = lexicon[word]
                if wid not in docs[-1].content:
                    docs[-1].content[wid] = []
                docs[-1].content[wid].append(loc)
                loc += 1
                word = ""

    # save lexicon in a file
    a_file = open("Lexicon.pkl", "wb")
    pickle.dump(lexicon, a_file)
    a_file.close()


def createInvertedIndex():
    # dict to store inverted index
    invertedIndex = {}

    for wd in lexicon:
        wid = lexicon[wd]
        # if word is not in the inverted index create an empty list for it
        if wid not in invertedIndex: # can be removed ******
            invertedIndex[wid] = []
        for i in range(len(docs)):
            rank = 0
            hits = 0
            # flag indicates if a word has been found in a particular document
            flag = False
            # if the word in title calculate hits and rank
            if wid in docs[i].title:
                hits += len(docs[i].title[wid])
                rank += hits * 5
                flag = True
            # if the word in content calculate hits and rank
            if wid in docs[i].content:
                hits += len(docs[i].content[wid])
                rank += hits * 3
                flag = True
            if flag:    # can be checked if rank = 0
                # if flag is true append the docId, rank and hits for that word
                invertedIndex[wid].append(ForwardIndex.Hits(i, rank, hits))
            flag = False

    # create file and add invertedIndex to the file
    a_file = open("InvertedIndex.pkl", "wb")
    pickle.dump(invertedIndex, a_file)
    a_file.close()


snow_stemmer = SnowballStemmer(language='english')
cwd = os.getcwd()
docs = []
lexicon = {'told': 0}
files = [one for one in os.listdir(cwd) if one.endswith('.json')]  # get all json files in current working directory
start_time = time.time()
# update lexicon, forward index and inverted index for every document
for z in files:
    myjsonfile = open(z, 'r')
    jsondata = myjsonfile.read()
    obj = json.loads(jsondata)
    myjsonfile.close()
    updateLexicon(obj)
createInvertedIndex()
print("time:", time.time() - start_time, " seconds")
