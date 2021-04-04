# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

import re
from nltk.util import ngrams, pad_sequence, everygrams
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.lm import MLE, WittenBellInterpolated, Lidstone, Laplace
import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter
import nltk
from nltk.util import ngrams
from nltk.lm.preprocessing import pad_both_ends, padded_everygram_pipeline
from collections import defaultdict, Counter

nltk.download('punkt')

# %%
# set ngram number
ngram_length = 4


script = pd.read_csv("./data/lotr_script_extended.csv").drop("Unnamed: 0", axis=1)
script["scene_num"] = script["scene"].factorize()[0]
script["tokenized_line"] = [nltk.flatten([list(map(str.lower, word_tokenize(sent))) for sent in sent_tokenize(line)]) for line in script["text"]]
script["num_words"] = script["tokenized_line"].str.len()
script["num_words_ngrams"] = script["tokenized_line"].str.len() - 2*ngram_length + 2
script

# %%
# %%
with open("./data/books/01 - The Fellowship Of The Ring.txt", encoding='cp1250') as f:
    book1_text = f.read()

with open("./data/books/02 - The Two Towers.txt", encoding='cp1250') as f:
    book2_text = f.read()

with open("./data/books/03 - The Return Of The King.txt", encoding='cp1250') as f:
    book3_text = f.read()

books_text = book1_text + book2_text + book3_text

# Tokenize and pad the text
books_tokens = word_tokenize(books_text.lower())
books_data = list(ngrams(books_tokens, n=ngram_length))
#%%

books_dict = defaultdict(list)
for i, ngram in enumerate(books_data):
    books_dict[ngram].append(i)

print(len(books_dict))

# remove ngrams that occur more often than 2 times (cannot have much information if they are common)
keys = list(books_dict.keys())
for key in keys:
    if len(books_dict[key]) > 3:
        del books_dict[key]

print(len(books_dict))

# %%

script["occurances"] = [{} for _ in range(len(script))]
for i, tokenized_line in enumerate(script["tokenized_line"]):

    for ii, ngram in enumerate(ngrams(tokenized_line, n=ngram_length)):
        if ngram in books_dict:
            script.loc[i, "occurances"][ngram] = books_dict[ngram]


# %%
script["num_words_found_book"] = script["occurances"].str.len()


# %%
# cut book into chapters
chapter_starts = [0] + [i for i, x in enumerate(books_tokens) if x == "_chapter"]
chapter_titles = ["Prolog"] + re.findall(r"_Chapter\s[0-9]*_\n\s*(.*)", books_text)
books_data = pd.DataFrame([chapter_starts, chapter_titles], ["start", "name"]).T
books_data


scene_data = pd.DataFrame({"name": script["scene"].unique()})
scene_data["occurances"] = script.groupby("scene_num")["occurances"].apply(list)
scene_data["total_ngram_count"] = script.groupby("scene_num")["num_words_ngrams"].apply(sum)
scene_data

for chapter in books_data["name"]:
    scene_data[chapter] = 0
scene_data

def loc_to_chapter(loc):

    for i in range(len(books_data)-1):
        start = books_data["start"].iloc[i]
        end = books_data["start"].iloc[i+1]

        if start <= loc < end:
            return books_data["name"].iloc[i]

    if loc > books_data["start"].iloc[-1]:
        return books_data["name"].iloc[-1]
    
    raise ValueError("Loc not found")

# %%
# construct a text similar to TODO
corresponding_text = pd.DataFrame({"name": script["scene"].unique()})
for chapter in books_data["name"]:
    corresponding_text[chapter] = [[] for _ in range(len(scene_data))]

for i, combined_occurances in enumerate(scene_data["occurances"]):
    for occurances in combined_occurances:
        for ngram, occurance in occurances.items():
            for loc in occurance:
                # try to combine to text fragment

                try:
                    # map hits to correct scene
                    scene_data.loc[i, loc_to_chapter(loc)] += 1

                    # try to reconstruct complete sentence
                    prev_tokens = corresponding_text.loc[i, loc_to_chapter(loc)][-3:]
                    # print(corresponding_text.loc[i, loc_to_chapter(loc)])
                    # print(prev_tokens)
                    # print(list(ngram[:-1]))
                    # print(list(prev_tokens) == list(ngram[:-1]))
                    if prev_tokens == list(ngram[:-1]):
                        # print("found")
                        corresponding_text.loc[i, loc_to_chapter(loc)].append(ngram[ngram_length-1]) # append only 1 new token
                    else:
                        # print("not found")
                        # print(corresponding_text.loc[i, loc_to_chapter(loc)])
                        corresponding_text.loc[i, loc_to_chapter(loc)].append("<br>") # seperate and append new ngram
                        for n in ngram:
                            corresponding_text.loc[i, loc_to_chapter(loc)].append(n) # seperate and append new ngram (loop because weird error with pandas and lists)
                        # print(corresponding_text.loc[i, loc_to_chapter(loc)])
                    # print()

                except Exception as e:
                    print(e)
                    pass
corresponding_text = corresponding_text[chapter_titles].applymap(" ".join)

# %%

import plotly.graph_objects as go
num_scenes = len(scene_data)
num_chapters = len(chapter_titles)
fig = go.Figure(data=go.Heatmap(
                    z=scene_data[chapter_titles].T,
                    # y="Book Chapter", x="Movie Scene", color=f"Nr of copied lines of length {ngram_length}",
                    y=chapter_titles,
                    x=scene_data["name"],
                    text=corresponding_text[chapter_titles].T,
                    colorscale='Greens',
                    ))
fig.update_layout(
    title='How much copying is done in the Lord of The Rings Trilogy?',
    xaxis_title="Movie Scenes",
    yaxis_title="Book Chapters",
    yaxis_nticks=len(chapter_titles),
    xaxis_nticks=len(scene_data),

    )

fig.show()
