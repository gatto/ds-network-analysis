import pandas as pd
from extract import Count, SocialETL
from rich import print
from rich.console import Console
from rich.table import Table

Hashtag_Counts = dict[
    str, list[int, int, int]
]  # questo è un dict che ha "hashtag": [count_ukr, count_rus, count_pax]


def construct_query(hashtags: Hashtag_Counts) -> str:
    # takes a list of hashtags and returns a string (the query string)
    my_query = ""
    for item in hashtags:
        my_query = f"{my_query} OR #{item}"
    my_query = my_query[4:]
    return my_query


def extract_tags(list_of_tweets) -> list:
    # takes a list of dictionaries, each represents a hashtag appearing in a single tweet,
    # and returns a list of the hashtags appearing in that tweet
    results = []
    for my_dict in list_of_tweets:
        results.append(my_dict["tag"].lower())
    return results


tagmadre = {
    "proukr": "slavaukraini",
    "prorus": "istandwithputin",
    "pax": "stopwarinukraine",
}

query_madre = " OR ".join([f"#{x}" for x in tagmadre.values()])
m = SocialETL(
    query=f"({query_madre}) lang:en",
    pages=1,
    recent=False,
)

tweets_with_hashtag = m.df[["id", "entities.hashtags"]].dropna()
print(
    f"{len(m.df)} tweets retrieved\nwith query '{query_madre}'\nof which {len(tweets_with_hashtag)} tweets with at least 1 hashtag."
)

tweets_with_hashtag["entities.hashtags"] = tweets_with_hashtag["entities.hashtags"].map(
    eval
)

tweets_with_hashtag["tags"] = tweets_with_hashtag["entities.hashtags"].map(extract_tags)

tweets_with_hashtag = tweets_with_hashtag.drop(columns="entities.hashtags")

## create a dataframe with all hashtags and their scores
all_hashtags = set(tweets_with_hashtag["tags"].explode())

print(f"We have {len(all_hashtags)} hashtags.")

for row in tweets_with_hashtag["tags"]:
    try:
        if my_type != type(row):
            print("u fucked up")
    except:
        pass
    my_type = type(row)


def create_score(
    df: pd.DataFrame, one_hashtag: str, root_tags: dict
) -> list[float, float, float]:
    print(f"Looking for {one_hashtag}…")
    mask = df["tags"].apply(lambda x: one_hashtag in x)
    df = df[mask]
    print(f"I found {len(df)} tweets with {one_hashtag}")

    results = []
    for category in root_tags:
        selection = set((category, one_hashtag))
        scores = []
        temp_mask = df["tags"].apply(
            lambda x: all(item for item in selection if item in x)
        )
        temp_df = df[temp_mask]
        results.append(len(temp_df) / len(df))

    print(results)
    return results


all_hashtags_dict = {}
for hashtag in all_hashtags:
    # discard based on support
    pass
    # calculate scores only on hashtags with enough support
    all_hashtags_dict[hashtag] = create_score(tweets_with_hashtag, hashtag, tagmadre)
print(all_hashtags_dict)
all_hashtags_df = pd.DataFrame.from_dict(
    all_hashtags_dict, orient="index", columns=tagmadre
)
print(all_hashtags_df)

exit()

my_results = []
results = {"proukr": [], "prorus": [], "pax": []}
results_as_series = {}
my_tags = []


def characterize_hashtags(tweet: pd.Series, root_tags: dict) -> str:
    if root_tags["proukr"] in tweet["tags"]:
        return "proukr"
    elif root_tags["prorus"] in tweet["tags"]:
        return "prorus"
    elif root_tags["pax"] in tweet["tags"]:
        return "pax"


tweets_with_hashtag["class"] = tweets_with_hashtag.apply(
    characterize_hashtags, root_tags=tagmadre, axis=1
)

print(
    tweets_with_hashtag
)  # fatto alla fine:padre->score->k figli->score->del supp<=th->print(tweets_with_hashtags)
exit()

top_results_to_show = 10
top_results_to_take = 3
for category, value in results.items():
    results_as_series[category] = pd.Series(value, name=category)
    print(
        f"top {top_results_to_show} results for category {category} are:\n{results_as_series[category].value_counts()[:top_results_to_show]}"
    )
    to_append = results_as_series[category].value_counts()[:top_results_to_take].index
    to_append = [x for x in to_append]
    print(f"Hashtags we're taking for category {category} are: {to_append}\n")
    my_tags.extend(to_append)

# second iteration
## initialize the table
table = Table(title="Table of hashtags")
table.add_column("Hashtag", style="cyan", no_wrap=True)
table.add_column("Count in first search", justify="right", style="magenta")
table.add_column("Count in second search", justify="right", style="magenta")
table.add_column("Category assigned", style="green")
console = Console()


"""
match i:
    case 0 | 1:
        category = "proukr"
    case 2 | 3:
        category = "prorus"
    case 4 | 5:
        category = "pax"
table.add_row(item, str(results_as_series[category].value_counts()[item]), None, None)
"""

m = SocialETL(
    query=f"({my_query}) lang:en",
    pages=1,
    recent=False,
)

print(m.df)
print(m.df.info())

console.print(table)


"""
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
