# Stock Market

In this repository, I collect scripts and snippets to help me deal with the stock market.
So far, there are these scripts here:

- **wheel_profits** - keeps track of my profits and losses on the "Wheel" option strategy
- **dividends** - keeps track of the dividends I collect
- **nexo_interest** - sums up the interest received from Nexo and (TODO) converts it into another
  currency

## Wheel Profits

### Background

This script was heavily inspired by the
[In the Money](https://www.youtube.com/channel/UCfMiRVQJuTj3NpZZP1tKShQ) YouTube channel.
In one of his video tutorials, Adam presented the "Wheel" strategy for stock options trading
and provided a link to a Google spreadsheet in which he suggests you write down your trades
and track your progress.

Initially, I was indeed Adam's spreadsheet and wrote this script to read it in an get some more
insight into the data. At some point, reading in the sheet became way to slow, so I moved
to a text-based `.csv` system and adapted my script to read in those.
(It still can read the excel sheet, though it is no longer my preferred method and the code
no longer maintained.)
Importing the data from all the `.csv` files is much faster and I can much easier switch between
different tickers (by fuzzy-finding the file inside my texteditor instead of scrolling through the
spreadsheet tab bar and clicking).

### Data Files

Collect your option buy and sell data in `.csv` files in a dedicated directory.
The script takes a path as command line argument and will read all `*.csv` files in that directory.
I put trades from different stocks in separate files, though you could put everything into one file
or separate in time instead (e.g. each month its own file).
The files are expected to contain comma separated tables with the first line for the header.
The files are imported by `pandas` and the columns referred to by **name**, so make sure that the
following names are present:
```
Action,Date,# of Shares,Share Price,Status
```
Additional columns and order don't matter.
The script provides a `--new <ticker_name>` flag to create an otherwise empty file with a compliant
header for you.

Do be aware that you have to distinguish between debits and credits yourself!
You can enter negative values in the share price or number of shares columns as to your liking.
I want my bottom line to be positive when I *receive* money, so, when I sell an option contract,
I put `100` in the number of shares column and the premium received (per share) into the
share price column. When I buy the option back, `100` goes into the number column again and the
price I paid goes as a *negative* number into the share price column.

### Usage

Install the package with `pip install .` and run `wheel_profits.py` in the `scripts` folder.
You can provide a number of command line arguments -- some optional, some mandatory -- so you
probably want to wrap the python script again in a shell script, an alias or similar.

#### Data Source

Use `-d` to define a directory where to import all `*.csv` files from.
You can use `--tickers` to only import files whose basename (sans the `.csv` ending) matches the
given arguments.

#### Date Ranges

The start and end dates for the tally are inferred from the provided data,
using the earliest and latest found date, respectively.
You can narrow the time frame with the `-s, --start_date` and `-e, --end_date` flags.
The given dates are by default expected in ISO format: "YYYY-MM-DD", though the format can be
changed with the `-f` flag (format string according to python's `datetime`).
The time intervals (weeks, months etc.) are constructed using `pandas`.
That means for example, that when you are looking at weekly tallies, the constructed weeks will be
"calendar weeks" and your first week will be the one that starts with a Monday and contains your
`start_date`.

#### Skipping Actions

I do put stock buy, sell and LEAPS trades into my files but I usually don't want them to be
considered in my cash-flow calculations.
You can use `-a` to ignore entries whose "Action" entry `starts_with` any provided argument.

Those buy and sell orders will be used in the companion script `adjusted_cost_basis.py`, though.
