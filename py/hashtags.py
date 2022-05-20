import pandas as pd
from extract import Count, SocialETL


def extract_tags(value):
    results = []
    for my_dict in value:
        results.append(my_dict["tag"].lower())
    return results


m = SocialETL(query="Putin", pages=5, recent=True)
print(m.df["entities.hashtags"])

miao = m.df[["id", "entities.hashtags"]].dropna()
print(miao["entities.hashtags"])
print(miao.info())

miao["entities.hashtags"] = miao["entities.hashtags"].map(eval)

miao["tags"] = miao["entities.hashtags"].map(extract_tags)

my_results = []

tagmadre = {
    "proukr": "slavaukraini",
    "prorus": "istandwithputin",
    "pax": "stopwarinukraine",
}
results = {"proukr": [], "prorus": [], "pax": []}
miaone = {}

for _, riga in miao.iterrows():
    if tagmadre["proukr"] in riga["tags"]:
        #        results = [tag for tag in riga["tags"]]
        #        for tag in riga["tags"]:
        #            results.append(tag)
        results["proukr"].extend([tag for tag in riga["tags"]])
    elif tagmadre["prorus"] in riga["tags"]:
        results["prorus"].extend([tag for tag in riga["tags"]])
    elif tagmadre["pax"] in riga["tags"]:
        results["pax"].extend([tag for tag in riga["tags"]])
for category, value in results.items():
    miaone[category] = pd.Series(value, name=category)
    print(miaone[category])
    print(miaone[category].value_counts())


"""
df_pro["entities.hashtags"] = my_dict["entities.hashtags"].fillna("0")

repl = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    "start",
    "end",
    "tag",
    "[",
    "{",
    "}",
    "]",
    ":",
    ",",
    '"',
]
for e in repl:
    df_pro["entities.hashtags"] = df_pro["entities.hashtags"].str.replace(
        e, "", regex=True
    )
df_pro["entities.hashtags"] = df_pro["entities.hashtags"].apply(str).map(str.strip)
df_pro["entities.hashtags"] = (
    df_pro["entities.hashtags"].apply(str).map(str.split)
)  # ,args=('\"\"'))
df_hash = df_pro["entities.hashtags"]

hashtag = list()
size = len(df_hash)
for i in range(0, size):
    for e in df_hash[i]:
        if len(e) >= 4:
            hashtag.append(e)

tag = {}
for e in hashtag:
    tag[e] = hashtag.count(e)

tag_list = sorted((value, key) for (key, value) in tag.items())
tag_list = sorted(tag_list, key=lambda x: x[0], reverse=True)
tag_sorted = dict([(k, v) for v, k in tag_list])
print(tag_sorted)
"""
