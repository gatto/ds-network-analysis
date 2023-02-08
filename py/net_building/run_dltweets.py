import extract
import pandas as pd

open_nodes = pd.read_csv("df_nodes.csv")
ids = set(open_nodes["tweet_id"])
del open_nodes

a = extract.DownloadTweets(ids)
a.to_csv()
