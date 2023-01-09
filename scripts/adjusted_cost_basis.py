#!/usr/bin/env python

"""
Reads the csv files from a given directory and prints the assigned shares, adjusted cost basis
and other metrics per ticker symbol.
"""

from stock_market.read.csv_dir import read_csv_dir_wheel as read_csv_dir
from stock_market.tally.tally_table import get_acb_table
from stock_market.utils import new_ticker_wheel as new_ticker
import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("--tickers", nargs='*', type=str, default=[])
ap.add_argument("--skip_actions", nargs='*', type=str, default=[])
ap.add_argument("-n", "--new", type=str,
        help="create a new blank file for a given ticker symbol with only the csv header")

agroup = ap.add_mutually_exclusive_group()
agroup.add_argument("-a", "--assigned", default=False, action='store_true',
        help="show only assigned positions (holding sahres)")
agroup.add_argument("-u", "--unassigned", default=False, action='store_true',
        help="show only unassigned positions (holding no shares)")

args = vars(ap.parse_args())

if args["csv_directory"] is None:
    print("no data location given")
    exit(-1)

if args["new"]:
    new_ticker(args["new"], args["csv_directory"])
    exit(0)

# returns a dictionary with ticker symbol als key and pandas data frame as values
data_map = read_csv_dir(args["csv_directory"], args["tickers"])

# get the data frame with the adjusted cost basis for the requested ticker symbols
tally_table = get_acb_table(data_map, args["skip_actions"])

# filter for assigned or unassigned positions if requested
if args["assigned"]:
    tally_table = tally_table[tally_table.loc[:, "Shares"] > 0]
if args["unassigned"]:
    tally_table = tally_table[tally_table.loc[:, "Shares"] == 0]

print()
print(tally_table.sort_index())
print("\ntotal:", tally_table["Cashflow"].sum())
print()
