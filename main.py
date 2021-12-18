import json  # how to load json files
import pickle
import os
from pathlib import Path
import ForwardIndex
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import time


# create inverted index from the forward index barrles
def create_invertedindex():
    number_of_barrels = lexicon[list(lexicon)[-1]][0] // 500
    arr = [[0] * 500 for a in range(number_of_barrels + 1)]  # stores cumulative frequency of each barrel
    i = 0
    j = 0
    # get the cumulative frequency of words in each barrel
    for k in lexicon:
        if i == 0:
            arr[j][i] = lexicon[k][1]
            i += 1
        else:
            arr[j][i] = arr[j][i - 1] + lexicon[k][1]
            i += 1
            if i == 500:
                i = 0
                j += 1
    last = 0
    for index, a in enumerate(arr[number_of_barrels]):
        if a != 0:
            last = a
        else:
            arr[number_of_barrels][index] = last

    # store cumulative frequency
    a_file = open("arr.pkl", "wb")
    pickle.dump(arr, a_file)
    a_file.close()
    # sort each barrel using counting sort and store in file
    for i in range(number_of_barrels + 1):
        sizeofbarrel = arr[i][-1]
        listinverted = [[''] * 3 for sb in range(sizeofbarrel)]
        fobj = open('ForwardIndex/'+str(i) + '.txt', 'r')
        for line in fobj:
            url, wid, hits = line.split('#')
            arr[i][int(wid)] -= 1
            listinverted[arr[i][int(wid)]][0] = url
            listinverted[arr[i][int(wid)]][2] = hits
            listinverted[arr[i][int(wid)]][1] = wid
        fobj.close()
        with open('InvertedIndex/'+str(i) + '.txt', 'w') as wobj:
            for f in listinverted:
                wobj.write(str(f[0] + '#' + f[1] + '#' + f[2]))


# divide words of one article into barrels according to wordID
def create_forwardindex(fwdix, single):
    docid.append(single['url'])
    for wid, hits in fwdix.items():
        binid = wid // 500  # div of wid by 500 will be our barrelID in which the word id will be stored
        newid = wid % 500 # wid mod 500 is the difference from the smallest wordID in a barrel
        if binid not in barrels:
            barrels[binid] = open('ForwardIndex/'+str(binid)+'.txt', 'w')  # create barrel if don't exists

        # write documentID, wordID and hits for a word in a document in its corresponding barrel
        barrels[binid].write(str(len(docid)-1) + "#" + str(newid) + "#" + str(hits) + "\n")


# parse through articles then update lexicon and Forward Index
def update_data(obj):
    global lx_id
    # parse through each article and get words
    for i in range(len(obj)):
        fx = {}
        # get title from one article
        t = obj[i]['title']
        word = ""
        loc = 0
        # parse through title and select relevant words
        for cr in t:
            if cr.isalpha():
                word += cr
            else:
                if len(word) <= 2 or word in stop_words:
                    word = ""
                    continue
                word = word.lower()
                word = snow_stemmer.stem(word)
                # if word is not in lexicon then this word is added to lexicon with new word-id and '0' word count
                if word not in lexicon:
                    lexicon[word] = [lx_id, 0]
                    lx_id += 1

                wid = lexicon[word][0]

                hit = [1, loc] # make hit: '1' shows fancy hit, also add location of word in article
                loc += 1
                # if the word is found first time in an article then add its hit to fx and increment that word frequency
                if wid not in fx:
                    lexicon[word][1] += 1
                    fx[wid] = [hit]
                # if word is repeated in an article then append the new hit to the previous hits
                else:
                    fx[wid].append(hit)
                word = ""

        # get content from one article
        c = obj[i]['content']
        word = ""
        loc = 0
        # parse through content and select relevant words
        for cr in c:
            if cr.isalpha():
                word += cr
            else:
                if len(word) <= 2 or word in stop_words:
                    word = ""
                    continue
                word = word.lower()
                word = snow_stemmer.stem(word)
                # if word is not in lexicon then this word is added to lexicon with new word-id and '0' word count
                if word not in lexicon:
                    lexicon[word] = [lx_id, 0]
                    lx_id += 1

                wid = lexicon[word][0]

                # find hit. '0' shows plain hit, also add location of word in article
                hit = [0, loc]
                loc += 1
                if wid not in fx:
                    lexicon[word][1] += 1
                    fx[wid] = [hit]
                else:
                    fx[wid].append(hit)
                word = ""

        create_forwardindex(fx, obj[i])  # create forward index from fx dictionary


# set first word in lexicon. first element in array is word id second element is number of documents where this word
# exists
lexicon = {}
lx_id = 0
snow_stemmer = SnowballStemmer(language='english')

# get stopwords
a_file = open("stopwords.pkl", "rb")
stop_words = pickle.load(a_file)
a_file.close()

docid = []
barrels = {}

cwd = os.getcwd()
cwd += '/newsdata'
start_time = time.time()
files = [o for o in os.listdir(cwd) if o.endswith('.json')]   # get all json files in newsdata directory
# parse through the each json file and update lexicon and forwardIndex
for f in files:
    myjsonfile = open(cwd+'/'+f, 'r')
    jsondata = myjsonfile.read()
    fileobj = json.loads(jsondata)
    myjsonfile.close()  # *******add the first word of lexicon here
    update_data(fileobj)
    print(f)

# save lexicon
a_file = open("Lexicon.pkl", "wb")
pickle.dump(lexicon, a_file)
a_file.close()

# save docIds
a_file = open("docid.pkl", "wb")
pickle.dump(docid, a_file)
a_file.close()
print("time:", time.time()-start_time, "seconds")

# closing forward index files
for k in barrels:
    barrels[k].close()

create_invertedindex()

print("time:", time.time()-start_time, "seconds")
