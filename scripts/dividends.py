#!/usr/bin/env python

import argparse
from pathlib import Path

from stock_market.utils import polars_settings

from stock_market.read.ibkr import read_ibkr_folder
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

tgroup = ap.add_mutually_exclusive_group()
tgroup.add_argument("-m", "--monthly", default=False, action='store_true')
tgroup.add_argument("-q", "--quarterly", default=False, action='store_true')
tgroup.add_argument("-y", "--yearly", default=False, action='store_true')
tgroup.add_argument("-a", "--total", default=False, action='store_true')

args = vars(ap.parse_args())


dividends = read_ibkr_folder(Path(args["ibkr_directory"]))

if args["tickers"]:
    dividends = filter_tickers(dividends, args["tickers"])

if args["start_date"] or args["end_date"]:
    dividends = filter_dates(dividends, args["start_date"], args["end_date"])

# sum up dividends over the desired intervall (monthly by default)
for i, f in [
    ("total", sum_total),
    ("yearly", sum_yearly),
    ("quarterly", sum_quarterly),
    ("monthly", sum_monthly),
]:
    if args[i]:
        divis = f(dividends, "dividends")
        break
else:
    divis = sum_monthly(dividends, "dividends")

# and print the resulting table
print(divis)

# if not explicitly asked for, also print yearly tally
if f is not sum_yearly:
    print(sum_yearly(dividends, "dividends"))

# show a plot of quarterly time-series
if args["plot"]:
    plot(sum_quarterly(dividends, "dividends"), True)
