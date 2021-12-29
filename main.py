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

lx_id = 0
doc_count = 0
docid = [[]]
url_check = {}
barrels = {}


# finds distance between two words; gives rank according to how close the words are. Returns sorted list of doc-ids
def proximity_rank(final_list, fixdata, fixrank):
    # pass through every document in the temporary forward index
    for d_id, fix in fixdata.items():
        nums = len(fix)
        # in each document apply cartesian product of every unique word in the search
        for i in range(nums - 1):

            for j in range(i + 1, nums):
                carts = list(itertools.product(fix[i], fix[j]))
                tmin = 10000
                cmin = 10000
                # after cartesian product check which combination has the minimum distance in both title and content
                for k in carts:
                    if k[0][0] != k[1][0]:
                        continue
                    if k[0][0] == 10:
                        if abs(k[0][1] - k[1][1]) < tmin:
                            tmin = abs(k[0][1] - k[1][1])
                    if k[0][0] == 1:
                        if abs(k[0][1] - k[1][1]) < cmin:
                            cmin = abs(k[0][1] - k[1][1])
                # give rank according to the shortest distance between two words
                if tmin <= 3:
                    fixrank[d_id] += 20
                elif tmin <= 5:
                    fixrank[d_id] += 15
                elif tmin <= 8:
                    fixrank[d_id] += 5

                if cmin <= 3:
                    fixrank[d_id] += 10
                elif cmin <= 5:
                    fixrank[d_id] += 5
                elif cmin <= 8:
                    fixrank[d_id] += 3

    # sort the rank and append in final_list
    nprank = np.array(list(fixrank.items()))
    nprank = nprank[nprank[:, 1].argsort()]
    nprank = np.flip(nprank, 0)
    final_list = np.append(final_list, nprank, axis=0)

    return final_list


# prints the urls sorted by rank for the given word
def WordSearch(word):
    # priorities of documents on how many words mach by the search query
    thirdfix = {}  # highest priority
    secondfix = {}  # second priority
    firstfix = {}  # lowest priority

    # rank of each document in its priority dictionary
    thirdrank = {}
    secondrank = {}
    firstrank = {}

    # convert word to standard form and only include unique words which are in lexicon
    all_words = word.split(" ")
    all_words = [snow_stemmer.stem(wd.lower()) for wd in all_words]
    main_words = [wd for wd in all_words if wd in lexicon and wd not in stop_words]
    main_words = list(dict.fromkeys(main_words))
    # parse through each word and select documents in which these words occur. Priority is also set on how many words
    # in search occur in a particular document
    for wd in main_words:
        wid = lexicon[wd][0]
        barrelid = wid // 400
        offsetid = wid % 400
        # get the start and end location in inverted index with the help of cumulative frequency
        if offsetid == 0:
            start = 0
            end = accumulativefreq[barrelid][offsetid]
        else:
            start = accumulativefreq[barrelid][offsetid - 1]
            end = accumulativefreq[barrelid][offsetid]

        quality_rank = int(100000/lexicon[wd][1]) # this assigns weights to words based on how many documents they occur
        # parse through the lines in the inverted index and get rank and hit list
        for line in itertools.islice(filestreams[barrelid], start, end):
            did, _, rank, hits = line.split('#')
            did, rank, hits = int(did), int(rank), literal_eval(hits)
            rank += quality_rank

            # set priority of documents based on how many words in search words occur in the document
            if did in thirdfix:
                thirdfix[did].append(hits)
                thirdrank[did] += int(rank)
            elif did in secondfix:
                thirdfix[did] = secondfix[did]
                thirdfix[did].append(hits)
                thirdrank[did] = secondrank[did] + rank
                secondfix.pop(did)
                secondrank.pop(did)
            elif did in firstfix:
                secondfix[did] = firstfix[did]
                secondfix[did].append(hits)
                secondrank[did] = firstrank[did] + rank
                firstfix.pop(did)
                firstrank.pop(did)
            else:
                firstfix[did] = [hits]
                firstrank[did] = rank

        # go to the start of the inverted file for another word that may lie in the same barrel
        filestreams[barrelid].seek(0)

    final_list = np.array([[-1, -1]])  # stores the final sorted list of document-ids and rank

    # first choose from highest priority list "thirdrank". if the search results are less than 10 then move to new
    # priority.
    if len(thirdrank) != 0:
        final_list = proximity_rank(final_list, fixdata=thirdfix, fixrank=thirdrank)

    if len(final_list) <= 11 and len(secondrank) != 0:
        final_list = proximity_rank(final_list, fixdata=secondfix, fixrank=secondrank)

    if len(final_list) <= 11 and len(firstrank) != 0:
        final_list = proximity_rank(final_list, fixdata=firstfix, fixrank=firstrank)

    print(time.time() - start_time)
    final_length = len(final_list)
    if final_length == 1:
        print("No match for the search!")
    elif final_length <= 11:
        for i in range(1, final_length):
            print(docids[final_list[i][0]][0], final_list[i])
            print(docids[final_list[i][0]][1])
            print('')
    else:
        for i in range(1, 11):
            print(docids[final_list[i][0]][0], final_list[i])
            print(docids[final_list[i][0]][1])
            print('')

    return final_list


def update_invertedindex():
    global lexicon
    global lx_id
    global docid
    global url_check

    # load the previous lexicon and get the next wordid and document information
    if Path("Lexicon.pkl").is_file():
        with open("Lexicon.pkl", 'rb') as l:
            lexicon = pickle.load(l)
            lx_id = len(lexicon)
    if Path("docid.pkl").is_file():
        with open("docid.pkl", 'rb') as d:
            docid = pickle.load(d)
    # get the new file(s) and create forward index
    new_files = [o for o in os.listdir(os.getcwd()) if o.endswith('json')]
    for new_file in new_files:
        with open(new_file, 'r') as nf:
            f_obj = json.loads(nf.read())
            print(len(f_obj))
            update_data(f_obj)
    # save the updated lexicon and the updated document information
    u_file = open("Lexicon.pkl", "wb")
    pickle.dump(lexicon, u_file)
    u_file.close()

    u_file = open("docid.pkl", "wb")
    pickle.dump(docid, u_file)
    u_file.close()

    # update the inverted index
    create_invertedindex()


# create inverted index from the forward index barrles
def create_invertedindex():
    number_of_barrels = lexicon[list(lexicon)[-1]][0] // 400
    arr = [[0] * 400 for a in range(number_of_barrels + 1)] # stores cumulative frequency of each barrel
    # only get those barrels that we need to open for updating the inverted index
    binids = list(barrels.keys())
    # these barrels may have been in opened in any order in case of updating the forward index, so we need to sort them
    binids.sort()
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
    # only those barrels are sorted that are open during updating
    for i in binids:
        sizeofbarrel = arr[i][-1]
        listinverted = [[''] * 4 for sb in range(sizeofbarrel)]
        # no need to open the forward barrels again since they were opened while building/updating the forward index
        # forward files are opened in a+ mode so to read from to start we need to seek to the start of the file
        barrels[i].seek(0)
        fobj = barrels[i].readlines()
        for line in fobj:
            url, wid, rank, hits = line.split('#')
            arr[i][int(wid)] -= 1
            sortplace = arr[i][int(wid)]
            listinverted[sortplace][0] = url
            listinverted[sortplace][1] = wid
            listinverted[sortplace][2] = rank
            listinverted[sortplace][3] = hits
        barrels[i].close()
        with open('InvertedIndex/' + str(i) + '.txt', 'w') as wobj:
            for f in listinverted:
                wobj.write(str(f[0] + '#' + f[1] + '#' + f[2] + '#' + f[3]))


# divide words of one article into barrels according to wordID
def create_forwardindex(fwdix, single):
    docid.append([single['url'], single['title']])
    for wid, hits in fwdix.items():
        binid = wid // 400  # div of wid by 400 will be our barrelID in which the word id will be stored
        newid = wid % 400  # wid mod 400 is the difference from the smallest wordID in a barrel
        if binid not in barrels:
            barrels[binid] = open('ForwardIndex/' + str(binid) + '.txt', 'a+')  # create barrel if don't exists

        rank = int(np.sum(np.array(hits), axis=0)[0])  # calculate rank of one document and its one word
        # write documentID, wordID, rank and hits for a word in a document in its corresponding barrel
        barrels[binid].write(str(len(docid) - 1) + "#" + str(newid) + "#" + str(rank) + "#" + str(hits) + "\n")


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
                if len(word) <= 2 or word in stop_words:  # ******** use word.lower() before this
                    word = ""
                    continue
                word = word.lower()
                word = snow_stemmer.stem(word)
                # if word is not in lexicon then this word is added to lexicon with new word-id and '0' word count
                if word not in lexicon:
                    lexicon[word] = [lx_id, 0]
                    lx_id += 1

                wid = lexicon[word][0]

                hit = [10, loc]  # make hit: '10' shows fancy hit, also add location of word in article
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
                elif len(fx[wid]) <= 6:  # more than 6 hits in an article is not allowed
                    fx[wid].append(hit)
                word = ""

        create_forwardindex(fx, obj[i])  # create forward index from fx dictionary


if not os.path.exists('Lexicon.pkl'):
    cwd = os.getcwd()
    if not Path(cwd + "/ForwardIndex").is_dir():
        os.makedirs("ForwardIndex")
    if not Path(cwd + "/InvertedIndex").is_dir():
        os.makedirs("InvertedIndex")
    cwd += '/newsdata'
    start_time = time.time()
    files = [o for o in os.listdir(cwd) if o.endswith('.json')]  # get all json files in newsdata directory
    # parse through the each json file and update lexicon and forwardIndex
    for f in files:
        myjsonfile = open(cwd + '/' + f, 'r')
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

    # closing forward index files       *********


    create_invertedindex()

    print("time:", time.time() - start_time)
else:
    #update_invertedindex()

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
        filestreams.append(open("InvertedIndex/" + str(i) + ".txt", "r"))

    word = 'Which books should I read'
    start_time = time.time()
    final_list = WordSearch(word)  # search for the word
    # close files
    for i in range(len(accumulativefreq)):
        filestreams[i].close()

