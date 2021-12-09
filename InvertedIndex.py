import pickle
from pathlib import Path

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
        for i in range(len(fwdIdx)):
            if wid in fwdIdx[i].title:
                if wid not in invertedIndex:
                    invertedIndex[wid] = []
                invertedIndex[wid].append(i)
            elif wid in fwdIdx[i].content:
                if wid not in invertedIndex:
                    invertedIndex[wid] = []
                invertedIndex[wid].append(i)
            elif wid == fwdIdx[i].author:
                if wid not in invertedIndex:
                    invertedIndex[wid] = []
                invertedIndex[wid].append[i]
            elif wid == fwdIdx[i].source:
                if wid not in invertedIndex:
                    invertedIndex[wid] = []
                invertedIndex[wid].append[i]
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


createInvertedIndex()
print(invertedIndex[7])
