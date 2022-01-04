#!/usr/bin/env python

import pandas as pd
import argparse

from .read.csv_dir import read_csv_dir
from .tally.tally_table import get_tally_table
from .utils import utils, new_ticker

ap = argparse.ArgumentParser()
ap.add_argument("-x", "--excel_sheet", type=str, default=None)
ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("--tickers", nargs='*', type=str, default=[])
ap.add_argument("-s", "--start_date", type=str, default=None)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-f", "--date_format", type=str, default="%Y-%m-%d")
ap.add_argument("-a", "--skip_actions", nargs='*', type=str)
ap.add_argument("-t", "--skip_sheets", nargs='*', type=str)

ap.add_argument("-n", "--new", type=str,
        help="create a new blank file for a given ticker symbol with only the csv header")

tgroup = ap.add_mutually_exclusive_group()
tgroup.add_argument("--daily", default=False, action='store_true')
tgroup.add_argument("--weekly", default=False, action='store_true')
tgroup.add_argument("--monthly", default=False, action='store_true')
tgroup.add_argument("--quarterly", default=False, action='store_true')

args = vars(ap.parse_args())

if args["new"]:
    new_ticker.new_ticker(args["new"], args["csv_directory"])
    exit(0)

# getting interval string; weekly is default
interval = ([ key for key in ["daily",  "weekly", "monthly", "quarterly"] if args[key] ] + ["weekly"])[0]

# reading in the data
if args["excel_sheet"] is not None:
    from read.excel import read_excel, get_weekly_p_l
    # read in the excel spreadsheets document
    workbook = args["excel_sheet"]
    weekly_p_l = get_weekly_p_l(args)
    read_excel(workbook, weekly_p_l, args["skip_sheets"] or [], args["skip_actions"] or [])
    exit(0)

if args["csv_directory"] is None:
    print("no data location given")
    exit(-1)

# returns a dictionary with ticker symbol als key and pandas data frame as values
data_map = read_csv_dir(args["csv_directory"], args["tickers"])

# concatenate the data frames from all ticker symbols
data_frame = pd.concat([df for df in data_map.values()])

# if one is only interested in cash flow from options, e.g. buy, sell and LEAPS actions
# can be excluded here
if args["skip_actions"]:
    data_frame = utils.skip_actions(data_frame, args["skip_actions"])

tally_table = get_tally_table(data_frame, interval, args["start_date"], args["end_date"], format=args["date_format"])

print()
print(tally_table)
print("\ntotal:", tally_table["Profit"].sum())
print()
