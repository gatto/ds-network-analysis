from pathlib import Path

import attr
import pandas as pd
import pkg_resources

try:
    DATA_PATH = pkg_resources.resource_filename("socialetl", "data/")
except ModuleNotFoundError:
    DATA_PATH = "data/"


@attr.s
class SocialETL:
    df = attr.ib()

    @df.default
    def _df_default(self):
        # loading
        # my_df = self._load("hour")
        roows = [
            ("v", "mytext"),
            (1, "I am #SlavaUkraini"),
            (2, "my Putin is fire"),
            ("miao", "stop the war"),
        ]
        df = pd.DataFrame(roows, columns=["a", "text"])
        print(df.info())
        print(df)
        # transformation

        return df

    def _load(self, file):
        my_csv = Path(f"{DATA_PATH}{file}.csv")
        my_csv_pkl = Path(f"{DATA_PATH}{file}.pkl")
        try:
            pipi = pd.read_pickle(my_csv_pkl)
        except FileNotFoundError:
            pipi = pd.read_csv(my_csv)
        return pipi
