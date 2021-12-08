import pickle

a_file = open("Lexicon.pkl", "rb")
lexicon = pickle.load(a_file)
a_file.close()

a_file = open("fwdix.pkl",'rb')
fwdIdx = pickle.load(a_file)
a_file.close()

invertedIndex = {}

for wd in lexicon:
    wid = lexicon[wd]
    # print(wd)
    for i in range(len(fwdIdx)):
        if wd in fwdIdx[i].title:
            if wd not in invertedIndex:
                invertedIndex[wd] = []
            invertedIndex[wd].append[i]
            continue
        elif wd in fwdIdx[i].content:
            if wd not in invertedIndex:
                invertedIndex[wd] = []
            invertedIndex[wd].append[i]
            continue
        elif wd == fwdIdx[i].author:
            if wd not in invertedIndex:
                invertedIndex[wd] = []
            invertedIndex[wd].append[i]
            continue
        elif wd == fwdIdx[i].author:
            if wd not in invertedIndex:
                invertedIndex[wd] = []
            invertedIndex[wd].append[i]
print(invertedIndex)