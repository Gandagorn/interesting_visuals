# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly
import re

# prepare the raw data
# episode_df = pd.read_csv("data/title.episode.tsv", delimiter='\t')
# sp_df = episode_df[episode_df["parentTconst"] == "tt0121955"] # get all south park episodes
# rating_df = pd.read_csv("data/title.ratings.tsv", delimiter='\t').set_index("tconst")
# sp_rating = rating_df.reindex(sp_df["tconst"])

# sp_df = pd.concat((sp_df.set_index("tconst"), sp_rating), axis=1)
# sp_df["seasonNumber"] = pd.to_numeric(sp_df["seasonNumber"])
# sp_df["episodeNumber"] = pd.to_numeric(sp_df["episodeNumber"])
# sp_df = sp_df.set_index(["seasonNumber", "episodeNumber"]).sort_index()

# sp_df = sp_df.dropna()["averageRating"]
# sp_df.index.rename(["season", "episode"], inplace=True)
# dialoge_df = pd.read_csv("data/All-seasons.csv")

# dialoge_df.drop(dialoge_df[dialoge_df["Season"] == "Season"].index, inplace=True)
# dialoge_df["Season"] = pd.to_numeric(dialoge_df["Season"])
# dialoge_df["Episode"] = pd.to_numeric(dialoge_df["Episode"])
# dialoge_df = dialoge_df.set_index(["Season", "Episode"]).sort_index()

# dialoge_df.index.rename(["season", "episode"], inplace=True)
# dialoge_df.columns = (["character", "line"])
# dialoge_df

full_data = pd.read_csv("data/lotr_scripts.csv")
full_data
# %%
full_data[full_data["movie"] == "The Return of the King "].iloc[:50]

# %%
full_data.iloc[1570:1600]


# %%
for i, line in enumerate(full_data["dialog"]):

    if type(line) == str and "Merin" in line:
        print(line)
        print(i)
        print("--------")
# %%
import requests
from bs4 import BeautifulSoup

URL = 'http://www.ageofthering.com/atthemovies/scripts/fellowshipofthering1to4.php'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

# %%
book_1_urls = [
    "/atthemovies/scripts/fellowshipofthering1to4.php",
    "/atthemovies/scripts/fellowshipofthering5to8.php",
    "/atthemovies/scripts/fellowshipofthering9to12.php",
    "/atthemovies/scripts/fellowshipofthering13to16.php",
    "/atthemovies/scripts/fellowshipofthering17to20.php",
    "/atthemovies/scripts/fellowshipofthering21to24.php",
    "/atthemovies/scripts/fellowshipofthering25to28.php",
    "/atthemovies/scripts/fellowshipofthering29to32.php",
    "/atthemovies/scripts/fellowshipofthering33to36.php",
    "/atthemovies/scripts/fellowshipofthering37to40.php",
    "/atthemovies/scripts/fellowshipofthering41to44.php",
    "/atthemovies/scripts/fellowshipofthering45to46.php",
    ]


combined_data = pd.DataFrame(columns=["character", "text", "scene"])
for url in book_1_urls: #[3:4]:
    print(url)

    page = requests.get("http://www.ageofthering.com/" + url)
    soup = BeautifulSoup(page.content, 'html.parser')

    speakers = []
    texts = []
    scene_names = []

    speaker_found = False
    scene_found = False
    for i, table in enumerate(soup.find_all("table")):

        speaker = 0

        for ii, row in enumerate(table.find_all("td")):
            # print(row.text.strip())
            # print(row.text)
            # print(re.search(r"Scene\s[0-9]+", row.text))
            # print(re.search(r"Scene 1", row.text.strip()))
            # break
            if re.search(r"Scene\s[0-9]+", row.text):
                scene_found = True
                scene_name = row.text.strip().replace("\r\n", "")
                continue

            if not scene_found: continue
                
            if not speaker_found and row.get("valign") == "top" and row.get("colspan") == None:
                # print(row)
                speaker = row.text.strip().replace(":","")
                if speaker.isupper():
                    speakers.append(speaker)
                    speaker_found = True
                    scene_names.append(scene_name)

            elif speaker_found:
                # print(row)
                text = row.text.strip().replace("\r\n", "\n")
                text = re.sub(r"\(.*?\)", r"", text)
                texts.append(text)
                speaker_found = False

    # print(speakers)
    # print(texts)

    scene_data = pd.DataFrame({"character":speakers, "text":texts, "scene": scene_names})
    combined_data = pd.concat((combined_data, scene_data), axis=0)

combined_data    






# %%

len(speakers) 

# %%

