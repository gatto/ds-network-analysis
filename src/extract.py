import datetime
import os
import platform
from pathlib import Path

import pandas as pd
import pkg_resources
from attrs import define, field
from rich.progress import track
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
    query: str = field(default="slavaukraini")
    pages: int = field(default=1)
    secret: str = field(default=None)
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
            max_results=100,
        )

        # Default options for Dataframe converter
        converter = DataFrameConverter()

        i = 1
        for page in track(search_results, description="Downloading tweets…"):
            miao = converter.process([page])

            try:
                df = pd.concat([df, miao], ignore_index=True)
            except NameError:
                df = miao

            # Stop iteration prematurely, to only get 1 page of results.
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

    def _get_local_credentials(self):
        my_secret_path = Path().cwd().parent / "data/my_secrets.yaml"
        try:
            with open(my_secret_path) as f:
                print(f"Reading secret from {my_secret_path}…")
                miao = f.readline().rstrip("\n").lstrip("api_key: ")
                return miao
        except FileNotFoundError:
            pass
        raise FileNotFoundError(f"There was no secrets file in {my_secret_path}.")
