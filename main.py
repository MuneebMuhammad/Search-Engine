
import json # how to load json files
import pickle
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from pathlib import Path
import re
# updates lexicon taken from Lexicon.pkl and restore the new lexicon in Lexicon.pkl
def updateLexicon(obj):
    lexicon = {}
    together = []
    porter = nltk.PorterStemmer()
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

    for i in range(len(obj)):
        #convert title and content to lowercase
        obj[i]['title'] = obj[i]['title'].lower()
        obj[i]['content'] = obj[i]['content'].lower()

        # remove punctuations from title and content
        for l in obj[i]['title']:
            if l in punc[3]:
                obj[i]['title'] = obj[i]['title'].replace(l, ' ')
            elif l in punc:
                obj[i]['title'] = obj[i]['title'].replace(l, '')
        for l in obj[i]['content']:
            if l in punc[3]:
                obj[i]['content'] = obj[i]['content'].replace(l, ' ')
            elif l in punc:
                obj[i]['content'] = obj[i]['content'].replace(l, '')

        # words are tokenized and stemming words removed
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

# read json file
myjsonfile = open('21stcenturywire.json', 'r')
jsondata = myjsonfile.read()
fileObj = json.loads(jsondata)
myjsonfile.close()

updateLexicon(fileObj)

a_file = open("Lexicon.pkl", "rb")
output = pickle.load(a_file)
print((output))


