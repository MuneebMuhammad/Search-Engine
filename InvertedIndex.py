import pickle
from pathlib import Path

import ForwardIndex

a_file = open("Lexicon.pkl", "rb")
lexicon = pickle.load(a_file)
a_file.close()

a_file = open("fwdix.pkl", 'rb')
fwdIdx = pickle.load(a_file)
a_file.close()

invertedIndex = {}


def createInvertedIndex():
    for wd in lexicon:
        wid = lexicon[wd]
        if wid not in invertedIndex:
            invertedIndex[wid] = []
        for i in range(len(fwdIdx)):
            rank = 0
            flag = False
            if wid in fwdIdx[i].title:
                rank += len(fwdIdx[i].title[wid])*5
                flag = True
            if wid in fwdIdx[i].content:
                rank += len(fwdIdx[i].content[wid])*3
                flag = True
            if wid == fwdIdx[i].author:
                rank += 150
                flag = True
            if wid == fwdIdx[i].source:
                rank += 100
                flag = True
            if flag:
                invertedIndex[wid].append(ForwardIndex.Hits(i, rank))
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


# createInvertedIndex()
a_file = open("InvertedIndex.pkl", "rb")
invtdIndx = pickle.load(a_file)
a_file.close()
print(fwdIdx[0].title)
# print(invtdIndx[1][0].rank)
