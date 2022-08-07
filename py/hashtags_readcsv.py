import json
import keyword
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd
from extract import extract_tags
from rich import print
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
    threshold_support = 0.5 * len(df) / 10000  # set the threshold_support here!!

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
    tweets_with_hashtag = pd.read_csv(Path("twee_hash_800.csv"), index_col=0)

    # hashtags: EXPLODE *musica dei power ranger*
    all_hashtags = set(tweets_with_hashtag.columns)

    # keyword level: eliminate all python keywords from columns because otherwise we are in no man's land
    keywordsss = keyword.kwlist
    keywordsss.extend(keyword.softkwlist)
    all_hashtags = all_hashtags.difference(keywordsss)
    all_hashtags = all_hashtags.difference(set(("",)))

    # up to here we have only dealt with a dataframe of tweets. Now we switch to dataframe of hashtags

    # create a dataframe with all hashtags and their scores
    all_hashtags_as_dict = {}
    supp = {}
    for hashtag in track(all_hashtags):
        # discard based on support
        pass
        # calculate scores only on hashtags with enough support
        score = create_score(tweets_with_hashtag, hashtag, tagmadre)
        if score is not False:
            # score[0] is the scores, score[1] is the support
            all_hashtags_as_dict[hashtag] = score[0]
            supp[hashtag] = score[1]
    all_hashtags_df = pd.DataFrame.from_dict(
        all_hashtags_as_dict, orient="index", columns=tagmadre
    )

    # now, "categorize" hashtags. The hashtag gets the category of its max score,
    # as long as it is > `threshold_certainty`
    # TODO: remember that we still need to account for hashtag support
    # (i.e. number of tweets supporting that hashtag)
    threshold_certainty = 0.5
    tags_categorized = defaultdict(list)
    for hashtag, scores in all_hashtags_df.iterrows():
        # print(hashtag, scores)  # TODO: check if the scores are different enough among 3 categories
        # print(scores.idxmax(), scores.max())
        if scores.max() > threshold_certainty:
            tags_categorized[scores.idxmax()].append((hashtag, scores.max()))
            other_scores = set(scores).difference(set((scores.max(),)))
            for sco in other_scores:
                if scores.max() < 1.2 * sco:
                    print(f"Attention. For {hashtag} the scores are\n{scores}")

    # tags_categorized.sort(key=lambda x: x[1], reverse=True)
    """    tags_categorized = {
        k: sorted(v, key=lambda item: item[1], reverse=True)
        for k, v in tags_categorized.items()
    }"""

    return tags_categorized, supp


if __name__ == "__main__":
    # params
    top_results_to_take = 3
    pages_to_do = 300

    # set the initial "parent" hashtags for each category
    tag_madre = {
        "proukr": ["slavaukraini"],
        "prorus": ["istandwithputin"],
        "pax": ["stopwarinukraine"],
    }

    # code
    # first run
    end_results, tags_support = do_search(tag_madre, pages_to_do)

    # second run
    """
    end_results = {
        k: [x[0] for x in v[:top_results_to_take]] for k, v in end_results.items()
    }
    print("miao", end_results)
    end_results = do_search(end_results)
    """

    with open(f"hashtags_{pages_to_do}.json", "w", encoding="utf-8") as f:
        json.dump(end_results, f, ensure_ascii=False, indent=4)
    with open(f"supports_{pages_to_do}.json", "w", encoding="utf-8") as f:
        json.dump(tags_support, f, ensure_ascii=False, indent=4)
