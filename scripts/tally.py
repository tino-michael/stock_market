#!/usr/bin/env python

from pathlib import Path
from loguru import logger

import polars as pl

from stock_market.config import Settings

from stock_market.utils import polars_settings
from stock_market.tally import (
    sum_yearly, sum_quarterly, sum_monthly, sum_daily, sum_total,
    filter_tickers, filter_dates,
    filter_currencies
)


settings = Settings()  # pyright: ignore[reportCallIssue]
args = settings


if args.new:
    from stock_market.utils import new_ticker_options as new_ticker
    new_ticker(args.new, args.csv_directory)
    exit(0)

gain_col = "credit"

# TODO: use pydanitc_settings `no-...` mechanism
if args.do_options:
    do_what = "options"
elif args.do_dividends:
    do_what = "dividends"
else:
    do_what = "both"


credit_dfs = []
if args.do_options:
    if args.ibkr_directory is not None:
        from stock_market.read.ibkr import read_ibkr_options_dir
        options_ibkr = read_ibkr_options_dir(Path(args.ibkr_directory))
        credit_dfs.append(options_ibkr)

    if args.tasty_directory is not None:
        from stock_market.read.tasty import read_tasty_options_dir
        options_tasty = read_tasty_options_dir(Path(args.tasty_directory))
        credit_dfs.append(options_tasty)


if args.do_dividends:
    from stock_market.read.ibkr import read_ibkr_dividends_dir
    dividends_ibkr = read_ibkr_dividends_dir(Path(args.ibkr_directory))
    credit_dfs.append(dividends_ibkr)


if not credit_dfs:
    logger.warning("nothing found...")
    exit(-1)

credits = pl.concat(credit_dfs)

if args.currencies:
    credits = filter_currencies(credits, set(c.upper() for c in args.currencies))

if args.tickers:
    credits = filter_tickers(credits, set(t.upper() for t in args.tickers))

if args.start_date or args.end_date:
    credits = filter_dates(credits, args.start_date, args.end_date)


for i, func in [
    ("total", sum_total),
    ("yearly", sum_yearly),
    ("quarterly", sum_quarterly),
    ("daily", sum_daily),
    ("monthly", sum_monthly),
]:
    if vars(args)[i]:
        # `func` is now the function given by CLI arg,
        # so just exit the loop now (`func` keeps being set)
        # if no period is given through CLI, keeps the last one (i.e. monthly)
        break

profits_tally = func(credits, gain_col, yoy=args.table_yoy, bar=args.bar, last=args.last)

# and print the resulting table
print(profits_tally)

# if not explicitly asked for, also print yearly tally
if func is not sum_yearly:
    print(sum_yearly(credits, gain_col, yoy=args.table_yoy, bar=args.bar))


# show a plot of quarterly time-series
if args.plot or args.plot_yoy:
    from stock_market.plotting.plot import plot
    plot(sum_quarterly(credits, gain_col), what=gain_col, calc_yoy=args.plot_yoy)
