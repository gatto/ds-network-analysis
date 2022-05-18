import datetime
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
    secret: str = field()
    query: str = field(default="slavaukraini")
    df: pd.DataFrame = field(init=False)

    @df.default
    def _df_default(self):
        t = Twarc2(bearer_token=self.secret)

        # Start and end times must be in UTC
        # start_time = datetime.datetime(2022, 3, 21, 0, 0, 0, 0, datetime.timezone.utc)
        # end_time = datetime.datetime(2022, 3, 22, 0, 0, 0, 0, datetime.timezone.utc)

        # search_results is a generator, max_results is max tweets per page, 100 max for full archive search with all expansions.
        search_results = t.search_recent(
            query=self.query,
            max_results=1000,
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

    def _load(self, file):
        my_csv = Path(f"{DATA_PATH}{file}.csv")
        my_csv_pkl = Path(f"{DATA_PATH}{file}.pkl")
        try:
            pipi = pd.read_pickle(my_csv_pkl)
        except FileNotFoundError:
            pipi = pd.read_csv(my_csv)
        return pipi
