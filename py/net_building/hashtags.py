import json
import keyword
import unicodedata
from collections import defaultdict

import pandas as pd
from extract import SocialETL, construct_query_for_twarc, extract_tags
from rich import print
from rich.console import Console
from rich.progress import track


def ensure_latin(s):
    return (
        unicodedata.normalize("NFKD", s).encode("latin-1", "ignore").decode("latin-1")
    )


def construct_query_for_pandas(root_tags: list) -> str:
    my_query = " or ".join(root_tags)
    return my_query


def create_score(df: pd.DataFrame, one_hashtag: str, root_tags: dict) -> list:
    # takes a df of all tweets, each row is a tweet, each column is
    # a hashtag either [True | False] depending on whether the hashtag
    # is in the tweet. Takes one_hashtag, the hashtag to score, and
    # root_tags, a dict of {category: [hashtags]}
    # TODO: make it so it accepts a list of {category: [hashtags]} instead of just one
    threshold_support = 0.9 * len(df) / 10000  # set the threshold_support here!!

    if threshold_support < 1:
        threshold_support = 1
    # print(f"Looking for {one_hashtag} with support {threshold_support}…")
    mask = df[one_hashtag]
    df = df[mask]
    # print(f"I found {len(df)} tweets with {one_hashtag}")
    if len(df) < threshold_support:
        return False
    """for col in df:
        if df[col].any():
            print(f"We have {col} hashtag")"""
    results = []
    # START OF TESTING:
    """    print(df.info())
    print(df.describe())
    print(df.head())
    print(f"[purple]Dude, here's the breakdown:")
    for tag in root_tags.values():
        print(f"[blue]This is {tag[0]}:")
        print(df[tag[0]])"""
    for category, tag_madre in root_tags.items():
        try:
            my_query = construct_query_for_pandas(tag_madre)
            # print(f"The pandas query is: [red]{my_query}")
            temp_df = df.query(my_query)
            # print(f"Holy jezuz: {len(temp_df)} and {len(df)}")
            results.append(round(len(temp_df) / len(df), 4))
        except KeyError:
            results.append(0)

    # print(results)
    return (results, len(df))


def do_search(tagmadre, pages):
    # construct the initial query to Twarc
    query_madre = construct_query_for_twarc(tagmadre)
    m = SocialETL(
        query=f"({query_madre})",
        pages=pages,
        recent=False,
    )

    # dropping any tweets with no hashtags (I think)
    tweets_with_hashtag = m.df[["id", "entities.hashtags"]].dropna()
    print(
        f"{len(m.df)} tweets retrieved\nwith query '{query_madre}'\nof which {len(tweets_with_hashtag)} tweets with at least 1 hashtag."
    )

    # evaluate the string in "entities.hashtags" to an actual list of dicts
    tweets_with_hashtag["entities.hashtags"] = tweets_with_hashtag[
        "entities.hashtags"
    ].map(eval)

    # make a simple list of strings, one hashtag is one string, into column "tags"
    tweets_with_hashtag["tags"] = tweets_with_hashtag["entities.hashtags"].map(
        extract_tags
    )
    tweets_with_hashtag = tweets_with_hashtag.drop(columns="entities.hashtags")

    # hashtags: EXPLODE *musica dei power ranger*
    all_hashtags = set(tweets_with_hashtag["tags"].explode())

    # keyword level: eliminate all python keywords from columns because otherwise we are in no man's land
    keywordsss = keyword.kwlist
    keywordsss.extend(keyword.softkwlist)
    all_hashtags = all_hashtags.difference(keywordsss)
    all_hashtags = all_hashtags.difference(set(("",)))

    print(f"We have {len(all_hashtags)} unique hashtags.")

    tweets_with_hashtag.set_index("id", inplace=True)

    col_h = sorted(list(all_hashtags))
    df_h = pd.DataFrame(columns=col_h)
    tweets_with_hashtag = pd.concat([tweets_with_hashtag, df_h], axis=1)
    tweets_with_hashtag = tweets_with_hashtag.fillna(False)

    def assign_hashtag_to_tweet(row: pd.Series) -> pd.Series:
        for tag in row["tags"]:
            if tag in all_hashtags:
                row.loc[tag] = True
        return row

    tweets_with_hashtag = tweets_with_hashtag.apply(assign_hashtag_to_tweet, axis=1)
    tweets_with_hashtag = tweets_with_hashtag.drop(columns=["tags"])

    for madre in tagmadre.values():
        print(f"[red]Let's write the describe of column '{madre[0]}'")
        print(tweets_with_hashtag[madre[0]].describe())

    tweets_with_hashtag.to_csv(f"twee_hash_{pages}.csv")
    print("[green]All done.")


if __name__ == "__main__":
    # params
    top_results_to_take = 3
    pages_to_do = 800

    # set the initial "parent" hashtags for each category
    tag_madre = {
        "proukr": ["slavaukraini"],
        "prorus": ["istandwithputin"],
        "pax": ["stopwarinukraine"],
    }

    # code
    # first run
    do_search(tag_madre, pages_to_do)
