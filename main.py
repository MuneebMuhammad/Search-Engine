import json  # how to load json files
import pickle
import re
import os
import time
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer
import time
import string


def updateLexicon(obj):
    # parse through every article in each document
    for i in range(len(obj)):
        # parse through each character in title and collect alphabetical words with size greater than 3
        t = obj[i]['title']
        word = ""
        loc = 0
        for char in t:
            # append characters is character is alphabet
            if char.isalpha():
                word += char
            else:
                # if word size is less than 3 then discharge the word and start with new word
                if len(word) <= 3:
                    word = ""    # location can be incremented here *********
                    loc = loc + 1
                    continue
                word = word.lower()  # convert word to lower case
                word = snow_stemmer.stem(word)  # perform stemming on the word
                # if word is not in lexicon then add the word to lexicon with 'word id = word_id of last element in dictionary + 1'
                if word not in lexicon:
                    lexicon[word] = lexicon[(list(lexicon)[-1])] + 1
                wid = lexicon[word]
                hit = [1, loc]   # find hit. '1' shows fancy hit. '0' shows plain hit
                # add the word along with its location and article's url to inverted index
                if wid not in ix:  # changed ****
                    ix[wid] = {obj[i]['url']: [hit]}
                else:
                    if obj[i]['url'] in ix[wid]:
                        ix[wid][obj[i]['url']].append(hit)
                    else:
                        ix[wid][obj[i]['url']] = [hit]  # till here
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
                    loc += 1
                    continue
                word = word.lower()
                word = snow_stemmer.stem(word)
                if word not in lexicon:
                    lexicon[word] = lexicon[(list(lexicon)[-1])] + 1
                wid = lexicon[word]
                hit = [0, loc]
                # add the word along with its hits and article's url to inverted index
                if wid not in ix:
                    ix[wid] = {obj[i]['url']: [hit]}
                else:
                    if obj[i]['url'] in ix[wid]:
                        ix[wid][obj[i]['url']].append(hit)
                    else:
                        ix[wid][obj[i]['url']] = [hit]
                loc += 1
                word = ""

snow_stemmer = SnowballStemmer(language='english')
start_time = time.time()
# update lexicon, forward index and inverted index for every document

lexicon = {'told': 0}
ix = {}
cwd = os.getcwd()
cwd += '/newsdata'
files = [o for o in os.listdir(cwd) if o.endswith('.json')]   # get all json files in newsdata directory
# parse through each file and find inverted index
for f in files:
    myjsonfile = open(cwd+'/'+f, 'r')
    jsondata = myjsonfile.read()
    obj = json.loads(jsondata)
    myjsonfile.close()
    updateLexicon(obj)
    print(f)

# save lexicon in a file
a_file = open("Lexicon.pkl", "wb")
pickle.dump(lexicon, a_file)
a_file.close()

# save lexicon in a file
a_file = open("invertedindex.pkl", "wb")
pickle.dump(ix, a_file)
a_file.close()

print("time:", time.time() - start_time, " seconds")
