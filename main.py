import json  # how to load json files
import pickle
import os.path
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer
import time
import itertools
import numpy as np
from ast import literal_eval


snow_stemmer = SnowballStemmer(language='english')
lexicon = {}
# get stopwords
a_file = open("stopwords.pkl", "rb")
stop_words = pickle.load(a_file)
a_file.close()


# prints the urls sorted by rank for the gien word
def WordSearch(word):
    # convert word to standard form
    word = word.lower()

    word = snow_stemmer.stem(word)
    if word not in lexicon:
        print("no match for this word")
        return
    else:
        # get location of the word with the word-id.
        wid = lexicon[word][0]
        barrelid = wid // 400  # gives the barrel id
        offsetid = wid % 400   # gives in which position of cumulative frequency array the word is placed
        # get the start and end location in inverted index with the help of cumulative frequency
        if offsetid == 0:
            start = 0
            end = accumulativefreq[barrelid][offsetid]
        else:
            start = accumulativefreq[barrelid][offsetid-1]
            end = accumulativefreq[barrelid][offsetid]

        sortrank = []
        # parse through the lines from start to end and get rank and document id
        for line in itertools.islice(filestreams[barrelid], start, end):
            did, _, rank, _ = line.split('#')
            sortrank.append([int (did), int(rank)])
        sortrank = np.array(sortrank)
        orderrank = sortrank[sortrank[:, 1].argsort()]  # sort the ranks and document id on rank column
        print("time:", time.time() - start_time)
        if len(orderrank) > 10:
            for i in range(-1, -10, -1):
                print(docids[orderrank[i][0]], orderrank[i])
        else:
            for i in range(len(orderrank) -1, -1, -1):
                print(docids[orderrank[i][0]], orderrank[i])


# create inverted index from the forward index barrles
def create_invertedindex():
    number_of_barrels = lexicon[list(lexicon)[-1]][0] // 400
    arr = [[0] * 400 for a in range(number_of_barrels + 1)]  # stores cumulative frequency of each barrel
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
            if i == 400:
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
        listinverted = [[''] * 4 for sb in range(sizeofbarrel)]
        fobj = open('ForwardIndex/'+str(i) + '.txt', 'r')
        for line in fobj:
            url, wid, rank, hits = line.split('#')
            arr[i][int(wid)] -= 1
            sortplace = arr[i][int(wid)]
            listinverted[sortplace][0] = url
            listinverted[sortplace][1] = wid
            listinverted[sortplace][2] = rank
            listinverted[sortplace][3] = hits

        fobj.close()
        with open('InvertedIndex/'+str(i) + '.txt', 'w') as wobj:
            for f in listinverted:
                wobj.write(str(f[0] + '#' + f[1] + '#' + f[2] + '#' + f[3]))


# divide words of one article into barrels according to wordID
def create_forwardindex(fwdix, single):
    docid.append(single['url'])
    for wid, hits in fwdix.items():
        binid = wid // 400  # div of wid by 400 will be our barrelID in which the word id will be stored
        newid = wid % 400 # wid mod 400 is the difference from the smallest wordID in a barrel
        if binid not in barrels:
            barrels[binid] = open('ForwardIndex/'+str(binid)+'.txt', 'w')  # create barrel if don't exists

        rank = int(np.sum(np.array(hits), axis=0)[0])  # calculate rank of one document and its one word
        # write documentID, wordID, rank and hits for a word in a document in its corresponding barrel
        barrels[binid].write(str(len(docid)-1) + "#" + str(newid) + "#" + str(rank) + "#" + str(hits) + "\n")


# parse through articles then update lexicon and Forward Index
def update_data(obj):
    global lx_id
    # parse through each article and get words
    for i in range(len(obj)):
        if obj[i]['url'] in url_check:
            continue

        url_check[obj[i]['url']] = 0
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

                hit = [5, loc] # make hit: '5' shows fancy hit, also add location of word in article
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

                # find hit. '1' shows plain hit, also add location of word in article
                hit = [1, loc]
                loc += 1
                if wid not in fx:
                    lexicon[word][1] += 1
                    fx[wid] = [hit]
                elif len(fx[wid]) <=6:  # more than 6 hits in an article is not allowed
                    fx[wid].append(hit)
                word = ""

        create_forwardindex(fx, obj[i])  # create forward index from fx dictionary

if not os.path.exists('Lexicon.pkl'):
    lx_id = 0
    doc_count = 0
    docid = []
    url_check = {}
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
        myjsonfile.close()
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

    # closing forward index files
    for k in barrels:
        barrels[k].close()

    create_invertedindex()

    print("time:", time.time() - start_time)
else:

    filestreams = []

    # load lexicon
    a_file = open("Lexicon.pkl", "rb")
    lexicon = pickle.load(a_file)
    a_file.close()

    # load accumulative frequency of words
    a_file = open("arr.pkl", "rb")
    accumulativefreq = pickle.load(a_file)
    a_file.close()

    # load docid and its url
    a_file = open("docid.pkl", "rb")
    docids = pickle.load(a_file)
    a_file.close()

    # open file streams for all inverted index barrels
    for i in range(len(accumulativefreq)):
        filestreams.append(open("InvertedIndex/"+str(i)+".txt", "r"))

    word = 'hello'
    start_time = time.time()
    WordSearch(word)  # search for the word

    # close files
    for i in range(len(accumulativefreq)):
        filestreams[i].close()
