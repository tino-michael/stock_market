import pandas as pd
import numpy as np
import glob

import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("-f", "--files", nargs='*', type=str, default=[])
ap.add_argument("--usd_column", type=str, default="USD Equivalent",
    help="The column name in the csv files that denotes the USD value of the received interest")
ap.add_argument("-r", "--rates", type=str, default=None, help="csv file with conversion rates throughout the year")

args = vars(ap.parse_args())

files = []
if args["csv_directory"]:
    files += glob.glob(args["csv_directory"] + "/*")

if args["files"]:
    files += args["files"]

print(f"found these files:", files)

if args["rates"]:
    rates_df = pd.read_csv(args["rates"], index_col="Month")

total = 0
for f in files:
    df = pd.read_csv(f, parse_dates=["Date / Time"])[[args["usd_column"], "Date / Time"]]
    df[args["usd_column"]] = df[args["usd_column"]] \
        .apply(lambda x: x.replace('$','')) \
        .apply(lambda x: x.replace(',','')) \
        .astype(np.float64)

    if args["rates"]:
        df = df.groupby(df["Date / Time"].dt.month)[args["usd_column"]].sum()
        df = pd.Series(df.to_numpy() / rates_df.iloc[df.index-1, 0].to_numpy())
    else:
        df = df[args["usd_column"]]

    total += df.sum()

print(f"{total=:.2f}")
