import keyword
import sys

import pandas as pd
from extract import Count, SocialETL
from rich import print
from rich.console import Console
from rich.table import Table


def construct_query_for_twarc(root_tags: dict) -> str:
    # takes a dict of hashtags and returns a string (the query string) to pass to Twarc
    my_list = [y for x in root_tags.values() for y in x]
    return " OR ".join([f"#{x}" for x in my_list])


def construct_query_for_pandas(root_tags: list) -> str:
    my_query = " or ".join(root_tags)
    return my_query


def extract_tags(list_of_hashtags) -> list:
    # takes a list of dictionaries, each represents a hashtag appearing in a single tweet,
    # and returns a list of the hashtags appearing in that tweet
    results = []
    for my_dict in list_of_hashtags:
        ## here we clean any hashtags e.g. with lower()
        results.append(my_dict["tag"].lower())
    return results


def create_score(df: pd.DataFrame, one_hashtag: str, root_tags: dict) -> list:
    # takes a df of all tweets, each row is a tweet, each column is
    # a hashtag either [True | False] depending on whether the hashtag
    # is in the tweet. Takes one_hashtag, the hashtag to score, and
    # root_tags, a dict of {category: [hashtags]}
    # TODO: make it so it accepts a list of {category: [hashtags]} instead of just one
    threshold_support = 0.1 * len(df) / 100  ## set the threshold_support here!!

    if threshold_support < 1:
        threshold_support = 1
    print(f"Looking for {one_hashtag} with support {threshold_support}…")
    mask = df[one_hashtag]
    df = df[mask]
    print(f"I found {len(df)} tweets with {one_hashtag}")
    if len(df) < threshold_support:
        return False
    """for col in df:
        if df[col].any():
            print(f"We have {col} hashtag")"""
    results = []
    # START OF TESTING:
    print(df.info())
    print(df.describe())
    print(df.head())
    print(f"[purple]Dude, here's the breakdown:")
    for tag in root_tags.values():
        print(f"[blue]This is {tag[0]}:")
        print(df[tag[0]])
    for category, tag_madre in root_tags.items():
        try:
            my_query = construct_query_for_pandas(tag_madre)
            print(f"The pandas query is: [red]{my_query}")
            temp_df = df.query(my_query)
            print(f"Holy jezuz: {len(temp_df)} and {len(df)}")
            input("Waiting for cats to cross the street…")
            results.append(len(temp_df) / len(df))
        except KeyError:
            results.append(0)

    # print(results)
    return results


def characterize_hashtags(tweet: pd.Series, root_tags: dict) -> str:
    if root_tags["proukr"] in tweet["tags"]:
        return "proukr"
    elif root_tags["prorus"] in tweet["tags"]:
        return "prorus"
    elif root_tags["pax"] in tweet["tags"]:
        return "pax"


if __name__ == "__main__":
    ## set the initial "parent" hashtags for each category
    tagmadre = {
        "proukr": ["slavaukraini"],
        "prorus": ["istandwithputin"],
        "pax": ["stopwarinukraine"],
    }

    ## construct the initial query to Twarc
    query_madre = construct_query_for_twarc(tagmadre)
    m = SocialETL(
        query=f"({query_madre}) lang:en",
        pages=1,
        recent=False,
    )

    ## dropping any tweets with no hashtags (I think)
    tweets_with_hashtag = m.df[["id", "entities.hashtags"]].dropna()
    print(
        f"{len(m.df)} tweets retrieved\nwith query '{query_madre}'\nof which {len(tweets_with_hashtag)} tweets with at least 1 hashtag."
    )

    ## evaluate the string in "entities.hashtags" to an actual list of dicts
    tweets_with_hashtag["entities.hashtags"] = tweets_with_hashtag[
        "entities.hashtags"
    ].map(eval)

    ## make a simple list of strings, one hashtag is one string, into column "tags"
    tweets_with_hashtag["tags"] = tweets_with_hashtag["entities.hashtags"].map(
        extract_tags
    )
    tweets_with_hashtag = tweets_with_hashtag.drop(columns="entities.hashtags")

    ## hashtags: EXPLODE *musica dei power ranger*
    all_hashtags = set(tweets_with_hashtag["tags"].explode())

    ## keyword level: eliminate all python keywords from columns because otherwise we are in no man's land
    keywordsss = keyword.kwlist
    keywordsss.extend(keyword.softkwlist)
    all_hashtags.difference(keywordsss)

    print(f"We have {len(all_hashtags)} unique hashtags.")

    ## make a dict of {hashtag: False}
    all_hashtags_as_dict = {}
    for hashtag in all_hashtags:
        all_hashtags_as_dict[hashtag] = False

    my_db = []

    ## change {hashtag: False} to {hashtag: True} only for hashtags that appear in tweet, then append dict
    ## to list my_db, where {id: tweet_id} and {hashtag: True} for hashtags appearing in that tweet_id.
    for _, row in tweets_with_hashtag.iterrows():
        d = all_hashtags_as_dict.copy()
        for tag in row["tags"]:
            # because we don't want to include any hashtag that is removed at the keyword level:
            if tag in d:
                d[tag] = True
        d["id"] = row["id"]
        my_db.append(d)

    df = pd.DataFrame(
        my_db,
        columns=sorted(all_hashtags),
        index=[row["id"] for row in my_db],
        dtype="Sparse[bool]",
    )

    ## up to here we have only dealt with a dataframe of tweets. Now we switch to dataframe of hashtags

    """
    print(f"Dense is {sys.getsizeof(ser)} bytes")
    ser = pd.Series(data=d, dtype="Sparse[bool]")
    print(ser)
    print(f"Sparse is {sys.getsizeof(ser)} bytes")
    """

    ## create a dataframe with all hashtags and their scores
    all_hashtags_as_dict = {}
    for hashtag in all_hashtags:
        # discard based on support
        pass
        # calculate scores only on hashtags with enough support
        score = create_score(df, hashtag, tagmadre)
        if score is not False:
            all_hashtags_as_dict[hashtag] = score
    print(all_hashtags_as_dict)
    all_hashtags_df = pd.DataFrame.from_dict(
        all_hashtags_as_dict, orient="index", columns=tagmadre
    )
    print(all_hashtags_df)

    ## now, "categorize" hashtags. The hashtag gets the category of its max score,
    ## as long as it is > `threshold_certainty`
    ## TODO: remember that we still need to account for hashtag support
    ## (i.e. number of tweets supporting that hashtag)
    threshold_certainty = 0.5
    tags_categorized = {category: [] for category in tagmadre}
    for hashtag, scores in all_hashtags_df.iterrows():
        # print(hashtag, scores)  # TODO: check if the scores are different enough among 3 categories
        # print(scores.idxmax(), scores.max())
        if scores.max() > threshold_certainty:
            tags_categorized[scores.idxmax()].append((hashtag, scores.max()))

    sorted(tags_categorized, key=lambda x: x[1])
    print(tags_categorized)
    exit()

    my_results = []
    results = {"proukr": [], "prorus": [], "pax": []}
    results_as_series = {}
    my_tags = []

    tweets_with_hashtag["class"] = tweets_with_hashtag.apply(
        characterize_hashtags, root_tags=tagmadre, axis=1
    )

    print(
        tweets_with_hashtag
    )  # fatto alla fine:padre->score->k figli->score->del supp<=th->print(tweets_with_hashtags)

    top_results_to_show = 10
    top_results_to_take = 3
    for category, value in results.items():
        results_as_series[category] = pd.Series(value, name=category)
        print(
            f"top {top_results_to_show} results for category {category} are:\n{results_as_series[category].value_counts()[:top_results_to_show]}"
        )
        to_append = (
            results_as_series[category].value_counts()[:top_results_to_take].index
        )
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
