#!/usr/bin/env python

import argparse
from pathlib import Path

from stock_market.utils import polars_settings

from stock_market.read.options import read_options_dir, skip_actions

from stock_market.tally import (
    sum_yearly, sum_quarterly, sum_monthly, sum_total,
    filter_tickers, filter_dates
)

from stock_market.utils import new_ticker_wheel as new_ticker

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("-t", "--tickers", nargs='*', type=str, default=[])
ap.add_argument("-s", "--start_date", type=str, default=None)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-p", "--plot", default=False, action='store_true')
ap.add_argument("-a", "--skip_actions", nargs='*', type=str)
ap.add_argument(
    "-n", "--new", type=str,
    help="create a new blank file for a given ticker symbol with only the csv header")

tgroup = ap.add_mutually_exclusive_group()
tgroup.add_argument("--monthly", default=False, action='store_true')
tgroup.add_argument("--quarterly", default=False, action='store_true')
tgroup.add_argument("--yearly", default=False, action='store_true')
tgroup.add_argument("--total", default=False, action='store_true')

args = vars(ap.parse_args())

if args["new"]:
    new_ticker(args["new"], args["csv_directory"])
    exit(0)


options = read_options_dir(Path(args["csv_directory"]))

if args["tickers"]:
    options = filter_tickers(options, set(t.upper() for t in args["tickers"]))

if args["start_date"] or args["end_date"]:
    options = filter_dates(options, args["start_date"], args["end_date"])

if args["skip_actions"]:
    options = skip_actions(options, args["skip_actions"])

# sum up dividends over the desired intervall (monthly by default)
for i, f in [
    ("total", sum_total),
    ("yearly", sum_yearly),
    ("quarterly", sum_quarterly),
    ("monthly", sum_monthly),
]:
    if args[i]:
        opts = f(options, "profit")
        break
    else:
        opts = sum_monthly(options, "profit")

# and print the resulting table
print(opts)

# if not explicitly asked for, also print yearly tally
if f is not sum_yearly:
    print(sum_yearly(options, "profit"))
