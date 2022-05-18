import datetime
import os
import platform
from pathlib import Path

import pandas as pd
import pkg_resources
from attrs import define, field
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
from twarc_csv import DataFrameConverter

try:
    DATA_PATH = pkg_resources.resource_filename("socialetl", "data/")
except ModuleNotFoundError:
    DATA_PATH = "data/"


@define
class OneTweet:
    text: str = field()

    @text.default
    def _text_default(self):
        pass


@define
class SocialETL:
    secret: str = field(default=None)
    query: str = field(default="slavaukraini")
    df: pd.DataFrame = field(init=False)

    @df.default
    def _df_default(self):
        if self.secret is None:
            my_secret = self._get_local_credentials()
        else:
            my_secret = self.secret
        t = Twarc2(bearer_token=my_secret)

        # search_results is a generator, max_results is max tweets per page, 100 max for full archive search with all expansions.
        search_results = t.search_recent(
            query=self.query,
            max_results=10,
        )

        # Default options for Dataframe converter
        converter = DataFrameConverter()

        # Get all results page by page:
        for page in search_results:
            # Do something with the whole page of results:
            # print(page)
            # or alternatively, "flatten" results returning 1 tweet at a time, with expansions inline:
            df = converter.process([page])

            # Stop iteration prematurely, to only get 1 page of results.
            break

            for tweet in ensure_flattened(page):
                # Do something with the tweet
                print(tweet)

        # TODO: transformation

        return df

    def is_interesting(self, tweet: OneTweet) -> bool:
        if tweet:  # condition of interestingness
            return True
        else:
            return False

    def _get_local_credentials(self):
        my_secret_path = Path().cwd().parent() / "data/my_secrets.txt"
        try:
            with open(my_secret_path) as f:
                print(f"Reading secret from {my_secret_path}…")
                return f.readline()
        except FileNotFoundError:
            pass
        raise FileNotFoundError(f"There was no secrets file in {my_secret_path}.")
