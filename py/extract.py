import datetime
import os
import platform
import random
from pathlib import Path

import pandas as pd
import pkg_resources
from attrs import define, field
from rich.progress import Progress, track
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
from twarc_csv import DataFrameConverter

try:
    DATA_PATH = pkg_resources.resource_filename("socialetl", "data/")
except ModuleNotFoundError:
    DATA_PATH = "data/"


def _get_local_credentials():
    my_secret_path = Path().cwd().parent / "data/my_secrets.yaml"
    try:
        with open(my_secret_path) as f:
            print(f"Reading secret from {my_secret_path}…")
            miao = f.readline().rstrip("\n").lstrip("api_key: ")
            return miao
    except FileNotFoundError:
        pass
    raise FileNotFoundError(f"There was no secrets file in {my_secret_path}.")


@define
class OneTweet:
    text: str = field()

    @text.default
    def _text_default(self):
        pass


@define
class SocialETL:
    query: str = field(default=None)
    recent: bool = field(default=False)
    pages: int = field(default=1)
    place: int = field(default=None)
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
                    2022, 2, 24, 0, 0, 0, 0, datetime.timezone.utc
                ),
            )
        converter = DataFrameConverter()

        with Progress() as progress:
            task = progress.add_task("Downloading 🐦…", total=self.pages)
            i = 1

            for page in search_results:
                miao = converter.process([page])

                try:
                    df = pd.concat([df, miao], ignore_index=True)
                except NameError:
                    df = miao

                progress.advance(task)
                if i == self.pages:
                    break
                i += 1

        # TODO: transformation

        return df

    def is_interesting(self, tweet: OneTweet) -> bool:
        if tweet:  # condition of interestingness
            return True
        else:
            return False


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
                2022, 2, 24, 0, 0, 0, 0, datetime.timezone.utc
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


class geo:
    lat: float = field(default=None)
    lon: float = field(default=None)
    query: str = field(default=None)
    ip: str = field(default=None)  # use the ip address to locate places
    granularity: str = field(
        default="neighborhood"
    )  # neighborhood, city, admin, country
    max_results: int = field(default=100)
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
                    2022, 2, 24, 0, 0, 0, 0, datetime.timezone.utc
                ),
            )


@define
class SocialDB:
    n: int
    df: pd.DataFrame = field()

    @df.default
    def _df_default(self):
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
        print(df.info())
        return df
