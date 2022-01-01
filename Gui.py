import pickle
import webbrowser
from tkinter import *
from tkinter import filedialog
from tkHyperLinkManager import HyperlinkManager
import Searcher
import Indexer
from functools import partial


def onClickSearch():
    i = 0
    searched_text = textBox.get()
    results = Searcher.WordSearch(searched_text, filestreams, lexicon, docids, accumulativefreq)
    textView.delete(0.0, END)
    hyperLink = HyperlinkManager(textView)

    while i < len(results):
        textView.insert(END, results[i])
        textView.insert(END, "\n")
        i += 1
        textView.insert(END, results[i], hyperLink.add(partial(webbrowser.open, results[i])))
        textView.insert(END, "\n")
        i += 1


def onClickInsert():
    filepath = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Json files",
                                                      "*.json*"),
                                                     ("all files",
                                                      "*.*")))
    Indexer.update_invertedindex(filepath)


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

window = Tk()
window.title('Search')
window.configure(background="white")
window.geometry("1920x1080")

insertButton = Button(window, text="Insert file", font=("Terminal", 10), width=11, command=onClickInsert)

insertButton.place(relx=0.9, rely=0.05, anchor="ne")
frame = Frame(window)
frame.pack()

textBox = Entry(frame, width=60, font=("Terminal", 14), bg="white")
textBox.pack(side=RIGHT)

searchButton = Button(frame, text="Search", font=("Terminal", 10), width=6, command=onClickSearch)

searchButton.pack(side=RIGHT)

frame.place(relx=0.25, rely=0.05, anchor="n")

scroll = Scrollbar(window)
scroll.pack(side=RIGHT, fill=Y)

textView = Text(window, width=120, height=25, background="white", font=("Segoe UI Semibold", 14),
                yscrollcommand=scroll.set)
textView.place(relx=0.44, rely=0.5, anchor=CENTER)

scroll.config(command=textView.yview)

# to show the window
window.mainloop()
# close files
for i in range(len(accumulativefreq)):
    filestreams[i].close()