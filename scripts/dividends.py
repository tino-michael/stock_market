#!/usr/bin/env python

import argparse
from pathlib import Path

from stock_market.utils import polars_settings

from stock_market.read.ibkr import read_ibkr_directory
from stock_market.tally import (
    sum_yearly, sum_quarterly, sum_monthly, sum_total,
    filter_tickers, filter_dates
)
from stock_market.plotting.plot import plot


ap = argparse.ArgumentParser()
ap.add_argument(
    "-d", "--ibkr_directory", type=str, required=True,
    help="Directory with the IBKR dividend exports in .csv format")
ap.add_argument("-t", "--tickers", nargs='*', type=str, default=[])
ap.add_argument("-s", "--start_date", type=str, default=None)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-p", "--plot", default=False, action='store_true')
ap.add_argument("--plot_yoy", default=False, action='store_true')
ap.add_argument("--table_yoy", default=False, action='store_true')

ap.add_argument("-l", "--last", default=None, type=int)

tgroup = ap.add_mutually_exclusive_group()
tgroup.add_argument("-m", "--monthly", default=False, action='store_true')
tgroup.add_argument("-q", "--quarterly", default=False, action='store_true')
tgroup.add_argument("-y", "--yearly", default=False, action='store_true')
tgroup.add_argument("-a", "--total", default=False, action='store_true')

args = vars(ap.parse_args())


dividends = read_ibkr_directory(Path(args["ibkr_directory"]))

if args["tickers"]:
    dividends = filter_tickers(dividends, set(t.upper() for t in args["tickers"]))

if args["start_date"] or args["end_date"]:
    dividends = filter_dates(dividends, args["start_date"], args["end_date"])

# sum up dividends over the desired intervall (monthly by default, i.e. last entry in option list)
for i, func in [
    ("total", sum_total),
    ("yearly", sum_yearly),
    ("quarterly", sum_quarterly),
    ("monthly", sum_monthly),
]:
    if args[i]:
        # `func` is now the function given by CLI arg,
        # so just exit the loop now (`func` keeps being set)
        break

divis = func(dividends, "dividends", args["table_yoy"], args["last"])

# and print the resulting table
print(divis)

# if not explicitly asked for, also print yearly tally
if func is not sum_yearly:
    print(sum_yearly(dividends, "dividends", args["table_yoy"]))

# show a plot of quarterly time-series
if args["plot"] or args["plot_yoy"]:
    plot(sum_quarterly(dividends, "dividends"), args["plot_yoy"])
