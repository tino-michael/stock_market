#!/usr/bin/env python

import argparse
import pandas as pd

from stock_market.utils import new_ticker_div as new_ticker
from stock_market.read.csv_dir import read_csv_dir_div as read_csv_dir
from stock_market.tally.tally_table import get_dividend_tally

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("--tickers", nargs='*', type=str, default=[])
ap.add_argument("-s", "--start_date", type=str, default=None)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-f", "--date_format", type=str, default="%Y-%m-%d")

ap.add_argument("-n", "--new", type=str,
        help="create a new blank file for a given ticker symbol with only the csv header")

tgroup = ap.add_mutually_exclusive_group()
tgroup.add_argument("--daily", default=False, action='store_true')
tgroup.add_argument("--weekly", default=False, action='store_true')
tgroup.add_argument("--monthly", default=False, action='store_true')
tgroup.add_argument("--quarterly", default=False, action='store_true')

args = vars(ap.parse_args())

if args["new"]:
    new_ticker(args["new"], args["csv_directory"])
    exit(0)

# getting interval string; monthly is default
interval = ([ key for key in ["daily",  "weekly", "monthly", "quarterly"] if args[key] ] + ["monthly"])[0]

# returns a dictionary with ticker symbol als key and pandas data frame as values
data_map = read_csv_dir(args["csv_directory"], args["tickers"])

# concatenate the data frames from all ticker symbols
data_frame = pd.concat([df for df in data_map.values()])

# calculate dividends from given tickers partitioned by date intervals
div_table = get_dividend_tally(data_frame, interval)

print(div_table)
