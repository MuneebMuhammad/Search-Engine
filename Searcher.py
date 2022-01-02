import itertools
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from ast import literal_eval

snow_stemmer = SnowballStemmer(language='english')


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
                    fixrank[d_id] += 25
                elif tmin <= 5:
                    fixrank[d_id] += 20
                elif tmin <= 8:
                    fixrank[d_id] += 15

                if cmin <= 3:
                    fixrank[d_id] += 15
                elif cmin <= 5:
                    fixrank[d_id] += 10
                elif cmin <= 8:
                    fixrank[d_id] += 5

    # sort the rank and append in final_list
    nprank = np.array(list(fixrank.items()))
    nprank = nprank[nprank[:, 1].argsort()]
    nprank = np.flip(nprank, 0)
    final_list = np.append(final_list, nprank, axis=0)

    return final_list


# prints the urls sorted by rank for the given word
def WordSearch(word,filestreams,lexicon,docids,accumulativefreq):
    results = []
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
    main_words = [wd for wd in all_words if wd in lexicon]
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

    if len(final_list) <= 50 and len(secondrank) != 0:
        final_list = proximity_rank(final_list, fixdata=secondfix, fixrank=secondrank)

    if len(final_list) <= 50 and len(firstrank) != 0:
        final_list = proximity_rank(final_list, fixdata=firstfix, fixrank=firstrank)

    final_length = len(final_list)
    if final_length == 1:
        results.append("No match for the search!")
    elif final_length <= 50:
        for i in range(1, final_length):
            results.append(docids[final_list[i][0]][1])
            results.append(docids[final_list[i][0]][0])
    else:
        for i in range(1, 50):
            results.append(docids[final_list[i][0]][1])
            results.append(docids[final_list[i][0]][0])

    return results
