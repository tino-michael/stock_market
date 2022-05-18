import pandas as pd
import numpy as np
import glob

import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("-f", "--files", nargs='*', type=str, default=[])
ap.add_argument("--usd_column", type=str, default="USD Equivalent",
    help="The column name in the csv files that denotes the USD value of the received interest")

args = vars(ap.parse_args())

files = []
if args["csv_directory"]:
    files += glob.glob(args["csv_directory"] + "/*")

if args["files"]:
    files += args["files"]

print(f"found these files:", files)

value = 0
for f in files:
    value += pd.read_csv(f)[args["usd_column"]] \
        .apply(lambda x: x.replace('$','')) \
        .apply(lambda x: x.replace(',','')) \
        .astype(np.float64).sum()

print(f"{value=:.2f}")
