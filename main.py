import json  # how to load json files
import pickle
import os
from pathlib import Path
import ForwardIndex
from nltk.stem.snowball import SnowballStemmer
import time

# divide one article into barrels
def create_forwardindex(fwdix, single):
    for wid, hits in fwdix.items():
        binid = wid // 500  # div of wid by 500 will be our binid in which the word id will be stored
        with open(str(binid)+'.txt', 'a') as addobj:
            addobj.write(single['url'] + " " + str(wid) + " " + str(hits) + "\n")



def update_data(obj):
    for i in range(len(obj)):
        fx = {}
        loc = 0
        # add source of the article to the lexicon and forwardIndex dictionary
        srce = obj[i]['source']
        if srce not in lexicon:
            lexicon[srce] = [lexicon[list(lexicon)[-1]][0] + 1, 1]
        else:
            lexicon[srce][1] += 1
        hit = [1, loc]
        wid = lexicon[list(lexicon)[-1]][0]
        fx[lexicon[list(lexicon)[-1]][0]] = [hit]

        # get title from one article
        t = obj[i]['title']
        word = ""
        loc = 0
        # parse through title and select relevant words
        for cr in t:
            if cr.isalpha():
                word += cr
            else:
                if len(word) <= 3:
                    word = ""
                    continue
                word = word.lower()  # convert word to lower case
                word = snow_stemmer.stem(word)
                # if word is not in lexicon then this word is added to lexicon with new word-id and '1' word count
                if word not in lexicon:
                    lexicon[word] = [lexicon[list(lexicon)[-1]][0] +1, 1]
                # if word already exists then increment word count of that word
                else:
                    lexicon[word][1] += 1

                wid = lexicon[word][0]
                word = ""
                hit = [1, loc] #find hit. '1' shows fancy hit, '0' shows plain hit. also add location of word in article
                loc += 1
                if wid not in fx:
                    fx[wid] = [hit]
                else:
                    fx[wid].append(hit)

        # get content from one article
        c = obj[i]['content']
        word = ""
        loc = 0
        # parse through content and select relevant words
        for cr in c:
            if cr.isalpha():
                word += cr
            else:
                if len(word) <= 3:
                    word = ""
                    continue
                word = word.lower()  # convert word to lower case
                word = snow_stemmer.stem(word)
                # if word is not in lexicon then this word is added to lexicon with new word-id and '1' word count
                if word not in lexicon:
                    lexicon[word] = [lexicon[list(lexicon)[-1]][0] + 1, 1]
                # if word already exists then increment word count of that word
                else:
                    lexicon[word][1] += 1
                wid = lexicon[word][0]
                word = ""
                hit = [0, loc]  # find hit. '1' shows fancy hit, '0' shows plain hit. also add location of word in article
                loc += 1
                if wid not in fx:
                    fx[wid] = [hit]
                else:
                    fx[wid].append(hit)

        create_forwardindex(fx, obj[i])  # create forward index from fx dictionary


lexicon = {'told': [0, 0]}  # set first word in lexicon. first element in array is word id second element is frequency
snow_stemmer = SnowballStemmer(language='english')

cwd = os.getcwd()
cwd += '/newsdata'
start_time = time.time()
files = [o for o in os.listdir(cwd) if o.endswith('.json')]   # get all json files in newsdata directory
for f in files:
    myjsonfile = open(cwd+'/'+f, 'r')
    jsondata = myjsonfile.read()
    fileobj = json.loads(jsondata)
    myjsonfile.close()
    update_data(fileobj)
    print(f)

a_file = open("Lexicon.pkl", "wb")
pickle.dump(lexicon, a_file)
a_file.close()
print("time:", time.time()-start_time, "seconds")
