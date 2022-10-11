import datetime
import json
import logging
import os
import platform
import random
import unicodedata
from pathlib import Path

import pandas as pd
import pkg_resources
from attrs import define, field, validators
from rich import print
from rich.logging import RichHandler
from rich.progress import Progress, track
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
from twarc_csv import DataFrameConverter

try:
    DATA_PATH = pkg_resources.resource_filename("socialetl", "data/")
except ModuleNotFoundError:
    DATA_PATH = "data/"


FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


def ensure_latin(s):
    return (
        unicodedata.normalize("NFKD", s).encode("latin-1", "ignore").decode("latin-1")
    )


def classify_tweet(hashtags: list, root_tags: dict) -> str:
    """
    Tweet is classified according to majority of hashtags. If no hashtags are found among root_tags,
    then category is `dontcare`. If there is no majority, category is `None`.
    """
    my_scores = {k: 0 for k in root_tags}
    interesting_tags = set().union(*root_tags.values())
    for hashtag in hashtags:
        if hashtag in interesting_tags:
            if hashtag in root_tags["proukr"]:
                my_scores["proukr"] += 1
            elif hashtag in root_tags["prorus"]:
                my_scores["prorus"] += 1
            elif hashtag in root_tags["pax"]:
                my_scores["pax"] += 1
    my_cat = get_unique_max(my_scores)

    ## now we discriminate what we found
    # case of no interesting tags in hashtags:
    if sum(my_scores.values()) == 0:
        my_cat = "dontcare"

    topscore_repr = (
        "" if my_cat in ("dontcare", None) else f", with score {my_scores[my_cat]}"
    )
    log.warning(f"cat for hashtags {hashtags} is: {my_cat}{topscore_repr}")

    return my_cat


def get_unique_max(scores: dict):
    my_max = max(scores, key=scores.get)
    # we need to check that the max is unique
    cocco = 0
    for value in scores.values():
        if value == scores[my_max]:
            cocco += 1
    # and now we return, discriminating on whether the max was unique or not
    if cocco > 1:  # non unique maximum found
        return None
    elif cocco == 1:  # unique maximum found
        return my_max
    else:  # wut tis
        raise Exception(f"cocco {cocco}")


def classify_user(user_tweets_categories: list, root_tags: dict) -> str:
    """
    User is classified according to simple majority of tweets for their category. If no majority, returns None.
    """
    my_scores = {k: 0 for k in root_tags}
    my_scores["dontcare"] = 0
    for category in user_tweets_categories:
        # this if ignores any tweet classified as None in classify_tweet() -> get_unique_max():
        if category:
            match category:
                case "proukr":
                    my_scores["proukr"] += 1
                case "prorus":
                    my_scores["prorus"] += 1
                case "pax":
                    my_scores["pax"] += 1
                case "dontcare":
                    my_scores["dontcare"] += 1
                case _:
                    log.error(
                        f"Wut? Category {category} doesn't exist\nuser's tweets are classified as: {user_tweets_categories}"
                    )
                    return "error"

    return get_unique_max(my_scores)


def construct_query_for_twarc(root_tags: dict) -> str:
    # takes a dict of hashtags and returns a string (the query string) to pass to Twarc
    my_list = [y for x in root_tags.values() for y in x]
    return " OR ".join([f"#{x}" for x in my_list])


def extract_tags(list_of_hashtags) -> list:
    # takes a list of dictionaries, each represents a hashtag appearing in a single tweet,
    # and returns a list of the hashtags appearing in that tweet
    results = []
    for my_dict in list_of_hashtags:
        # here we clean any hashtags e.g. with lower()
        cleaned = my_dict["tag"].lower()
        cleaned = ensure_latin(cleaned)
        results.append(cleaned)
    return results


def load_tag_madre(k: int = 1000):
    with open(Path().cwd() / "list_hashtags.json", "r") as f:
        tag_madre = json.load(f)
    tag_madre = {a: [x[0] for x in b[:k]] for a, b in tag_madre.items()}

    # remember to extend the "tag_madre" with the original tag_madre
    if "slavaukraini" not in tag_madre["proukr"]:
        tag_madre["proukr"].append("slavaukraini")
    if "istandwithputin" not in tag_madre["prorus"]:
        tag_madre["prorus"].append("istandwithputin")
    if "stopwarinukraine" not in tag_madre["pax"]:
        tag_madre["pax"].append("stopwarinukraine")
    return tag_madre


def _get_local_credentials():
    my_secret_path = Path().cwd().parent.parent / "data/my_secrets.yaml"
    try:
        with open(my_secret_path) as f:
            print(f"Reading secret from {my_secret_path}…")
            miao = f.readline().rstrip("\n").lstrip("api_key: ")
            return miao
    except FileNotFoundError:
        pass
    raise FileNotFoundError(f"There was no secrets file in {my_secret_path}.")


@define
class SocialETL:
    query: str = field(default=None)
    recent: bool = field(default=False)
    pages: int = field(default=1)
    secret: str = field(default=None, repr=False)
    df: pd.DataFrame = field(init=False, repr=lambda x: "pd.DataFrame")

    @df.default
    def _df_default(self):
        # authenticate here
        if self.secret is None:
            my_secret = _get_local_credentials()
        else:
            my_secret = self.secret
        t = Twarc2(bearer_token=my_secret)

        # am I accessing or am I counting?
        if self.recent:
            search_results = t.search_recent(
                query=self.query,
                max_results=100,
            )
        else:
            search_results = t.search_all(
                query=self.query,
                max_results=100,
                start_time=datetime.datetime(
                    2022, 2, 15, 0, 0, 0, 0, datetime.timezone.utc
                ),
                end_time=datetime.datetime(
                    2022, 6, 15, 0, 0, 0, 0, datetime.timezone.utc
                ),
            )
        converter = DataFrameConverter(
            extra_input_columns="edit_history_tweet_ids,edit_controls.edits_remaining,edit_controls.editable_until,edit_controls.is_edit_eligible"
        )

        with Progress() as progress:
            task = progress.add_task("Downloading 🐦…", total=self.pages)
            i = 1

            for page in search_results:
                miao = converter.process([page])
                try:
                    df = pd.concat([df, miao], ignore_index=True)
                except NameError:
                    df = miao

                progress.update(task, advance=1, refresh=True)
                if i == self.pages:
                    break
                i += 1

        # TODO: transformation
        df.rename(columns=ensure_latin, inplace=True)

        return df


@define
class Count:
    query: str = field(default="slavaukraini")
    secret: str = field(default=None, repr=False)
    df: pd.DataFrame = field(init=False, repr=lambda x: "pd.DataFrame")
    count: int = field(init=False)

    @df.default
    def _df_default(self):
        # authenticate here
        if self.secret is None:
            my_secret = _get_local_credentials()
        else:
            my_secret = self.secret
        t = Twarc2(bearer_token=my_secret)

        search_results = t.counts_all(
            query=self.query,
            granularity="day",
            start_time=datetime.datetime(
                2022, 2, 15, 0, 0, 0, 0, datetime.timezone.utc
            ),
        )
        df = pd.DataFrame(
            self._unpack_counts(search_results),
            columns=("start", "end", "tweet_count"),
        )
        return df

    @count.default
    def _c_default(self):
        return self.df["tweet_count"].sum()

    def _unpack_counts(self, my_iterator):
        for page in track(my_iterator, description="Reading…"):
            for value in page["data"]:
                yield {
                    "start": value["start"],
                    "end": value["end"],
                    "tweet_count": value["tweet_count"],
                }


@define
class UserETL:
    id: int = field()
    pages: int = field(default=1)  # each page is max_results tweets
    max_results: int = field(init=False, default=20)
    secret: str = field(default=None, repr=False)
    df: pd.DataFrame = field(init=False, repr=lambda x: "pd.DataFrame")

    @df.default
    def _df_default(self):
        global df
        if self.secret is None:
            my_secret = _get_local_credentials()
        else:
            my_secret = self.secret
        t = Twarc2(bearer_token=my_secret)

        log.warning(f"executing userETL on {self.id}")
        search_results = t.search_all(
            query=f"from:{self.id} has:hashtags",
            start_time=datetime.datetime(
                2022, 2, 15, 0, 0, 0, 0, datetime.timezone.utc
            ),
            end_time=datetime.datetime(2022, 5, 15, 0, 0, 0, 0, datetime.timezone.utc),
            max_results=self.max_results,
        )
        converter = DataFrameConverter(
            extra_input_columns="edit_history_tweet_ids,edit_controls.edits_remaining,edit_controls.editable_until,edit_controls.is_edit_eligible"
        )

        with Progress() as progress:
            task = progress.add_task("Downloading 🐦…", total=self.pages)
            i = 1

            for page in search_results:
                miao = converter.process([page])

                try:
                    df = pd.concat([df, miao], ignore_index=True)
                except NameError:
                    df = miao

                progress.update(task, advance=1, refresh=True)
                if i == self.pages:
                    break
                i += 1

        # TODO: transformation

        return df


@define
class SocialDB:
    n: int = field(default=100)  # quanti utenti generiamo, solo se placeholder=True
    k: int = field(default=3)  # quanti top hashtag prendiamo per categoria
    pages: int = field(default=5)
    placeholder: bool = field(default=False)
    df: pd.DataFrame = field(init=False, repr=lambda x: "pd.DataFrame")
    edges = field(init=False, repr=lambda x: "edges: list")

    @df.default
    def _df_default(self):
        if self.placeholder:  # make fake df
            results = []
            categories = ("proukr", "prorus", "pax", "nocare")
            for _ in range(self.n):
                miao = {
                    "id": random.randint(100000, 999999),
                    "class": random.choice(categories),
                }
                results.append(miao)

            df = pd.DataFrame(results)
            df.set_index("id", inplace=True)
            df["class"] = df["class"].astype("category")
            return df
        else:
            with open(Path().cwd() / "hashtags_300.json", "r") as f:
                tag_madre = json.load(f)
            tag_madre = {a: [x[0] for x in b[: self.k]] for a, b in tag_madre.items()}

            # remember to extend the "tag_madre" with the original tag_madre
            if "slavaukraini" not in tag_madre["proukr"]:
                tag_madre["proukr"].append("slavaukraini")
            if "istandwithputin" not in tag_madre["prorus"]:
                tag_madre["prorus"].append("istandwithputin")
            if "stopwarinukraine" not in tag_madre["pax"]:
                tag_madre["pax"].append("stopwarinukraine")

            # make query
            print(f"Tag madre used:\n{tag_madre}")
            qu = construct_query_for_twarc(tag_madre)
            print(f"query: '{qu}'")
            m = SocialETL(query=qu, pages=self.pages)

            # classify tweets
            m.df["tags"] = m.df["entities.hashtags"].map(eval).map(extract_tags)
            m.df = m.df[["id", "tags", "author_id"]]
            m.df["tweet_class"] = m.df["tags"].apply(
                classify_tweet, root_tags=tag_madre
            )
            m.df["tweet_class"] = m.df["tweet_class"].astype("category")

            # m.df.info():
            # "id", "tags", "author_id", "tweet_class", "all_tweets_by_user", "user_class"

            # classify users
            users_df = pd.DataFrame(
                m.df.groupby("author_id")["tweet_class"].apply(list)
            )
            users_df.rename(columns={"tweet_class": "tweet_classes"}, inplace=True)
            users_df["class"] = users_df["tweet_classes"].apply(
                classify_user, root_tags=tag_madre
            )
            users_df["class"] = users_df["class"].astype("category")
            return users_df

    @edges.default
    def _edges_default(self):
        if self.placeholder:  # make fake df
            users = set(self.df.index)
            results = []
            for _ in range(self.n * 3):
                my_users = random.sample(users, 2)
                miao = {
                    "id": random.randint(100000, 999999),
                    "from": my_users[0],
                    "to": my_users[1],
                }
                results.append(miao)
            return results
        else:
            my_author_ids = set(self.df.index)
            results = []
            print(f"Downloading from {len(my_author_ids)} users.")
            with Progress() as progress:
                task = progress.add_task("Users 🐦…", total=len(my_author_ids))

                for author in my_author_ids:
                    u = UserETL(id=author, pages=5)
                    u.df = u.df.dropna(subset=["retweeted_user_id"])
                    u.df = u.df.query("retweeted_user_id in @my_author_ids")

                    my_edges = []
                    for retweeted_author_id_in_tweet in u.df["retweeted_user_id"]:
                        my_edges.append(
                            {
                                "id": "coccodì",
                                "from": author,
                                "to": retweeted_author_id_in_tweet,
                            }
                        )
                        progress.update(task, advance=1, refresh=True)

                    print(u.df)
                    print(f"[red]The edges I've extracted are[/red]:\n{my_edges}")
                    results.extend(my_edges)
            return results


@define
class CategorizeUsers:
    user_ids: set = field(validator=validators.instance_of(set), repr=False)
    users: dict = field(init=False)

    @users.default
    def _users_default(self):
        tag_madre = load_tag_madre()
        results = {}

        for user_id in self.user_ids:
            u = UserETL(id=user_id, pages=5)

            # classify tweets
            u.df = u.df[["id", "entities.hashtags", "author_id"]]
            u.df = u.df.dropna(subset=["entities.hashtags"])
            u.df["tags"] = u.df["entities.hashtags"].map(eval).map(extract_tags)
            u.df["tweet_class"] = u.df["tags"].apply(
                classify_tweet, root_tags=tag_madre
            )
            u.df["tweet_class"] = u.df["tweet_class"].astype("category")

            # log.warning(u.df)

            # classify users
            users_df = pd.DataFrame(
                u.df.groupby("author_id")["tweet_class"].apply(list)
            )
            results[user_id] = users_df["tweet_class"].apply(
                classify_user, root_tags=tag_madre
            )[0]
            # what if no majority? [0] is suspect above
        return results


if __name__ == "__main__":
    a = CategorizeUsers(
        user_ids=set(
            (1011495440, 1363208713432145925, 357142859, 1492093926303580160, 142535879)
        )
    )
    print(a)
