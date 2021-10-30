# Wheel Profits

This script calculates your weekly / monthly profits and/or losses you produced with your
options trading. It reads in an excel spreadsheet where you put in all your trades, and
extracts and distils all your credits and debits.

## Update

OK, so, with an ever growing spreadsheet with more and more tabs for the various stock tickers,
importing of the excel sheet became unbearably long.
So I exported my data into `csv` files and rewrote the script so it would read those instead.
(It still can read the excel sheet though it is no longer my preferred method.)
Importing the data from all the `csv`s is much faster and I can much easier switch between different
tickers (by fuzzy-finding the file instead of scrolling through the spreadsheet tab bar and clicking).
For now, I will keep the old "Usage" section here at the bottom but consider it "legacy" and won't
update it.

## Data

Collect your option buy and sell data in `csv` files in a dedicated directory.
The script takes a path as command line argument and will read all `*.csv` files in that directory.
I put trades from different stocks in separate files, though you could put everything into one file
or separate in time instead (e.g. each month its own file).
The files are expected to contain comma separated tables with the first line for the header.
The files are imported by `pandas` and the columns referred to by **name**, so make sure that the
following names are present:
```Action,Date,# of Shares,Share Price,Status
```
Additional columns and order don't matter.

Do be aware that you have to distinguish between debits and credits yourself!
You can enter negative values in the share price or number of shares columns as to your liking.
I want my bottom line to be positive when I *receive* money, so, when I sell an option contract,
I put `100` in the number of shares column and the premium received (per share) into the
share price column. When I buy the option back, `100` goes into the number column again and the
price I paid goes as a *negative* number into the share price column.

## Usage

### Dates

The script expects a starting date with the `-s` flag; an end date with `-e` is optional.
If no end date is given, the current date is assumed.
I might change this at some point so that dates might be inferred from the data itself...
The given dates are by default expected in ISO format: "YYYY-MM-DD", though the format can be
changed with the `-f` flag (format string according to python's `datetime`).
As one might guess, the start and end dates define the time span for which the data is evaluated.

### Data Source

Use `-d` to define a directory where to import all `*.csv` files from.
You can use `--tickers` to only import files whose basename (sans the `.csv` ending) matches the
given arguments.

### Skipping Actions

I do put stock buy, sell and LEAPS trades into my files but I usually don't want them to be considered
in my cash-flow calculations.
You can use `-a` to ignore entries whose "Action" entry `starts_with` any provided argument.

## TODOs

- [ ] adjusted cost-basis calculation similar to what is done in the Google sheet
- [x] add `daily`, `weekly`, `monthly`, `quarterly`, `yearly` flags
- [x] be smarter about time-range calculations: completely done in pandas now


## Wrapping up

In the end, you probably want to wrap the script with all your specific arguments into a
shell script or an alias like so:

```bash
#!/bin/sh

BIN="/path/to/this/python/script.py"
SHEETS="/path/to/your/csv/directory/"
$BIN \
    -s 2021-02-01 \
    -d ${SHEETS} \
    --skip_actions buy sell L \
    $@
```

## Background

This script was heavily inspired by the [In the Money](https://www.youtube.com/channel/UCfMiRVQJuTj3NpZZP1tKShQ)
YouTube channel. In one of his video tutorials, Adam presented the "Wheel" strategy for
stock options trading and provided a link to a convenient Google spreadsheet
([click here](https://docs.google.com/spreadsheets/d/1mUJYD9jdVeEl-dwTfq2aXiPINf8698OehsSe34xOUfc/edit?usp=sharing) for my version with updated formatting).
This spreadsheet can be exported and/or published (copy to your own Google Drive, then:
File -> Publish to the web) as an excel document which then can be read by this here python script.

## Usage (legacy)

For the script to work, you need to provide a start date (`-s`) and the path to the excel
document (`-x`, which can be online). You can provide an end date if you like (`-e`),
by default the current day will be used. The dates for these flags are assumed to be formatted according
to ISO: YYYY-MM-DD; but this can be overwritten (`-f`, format string according to python's `datetime`).
By default, the tally is calculated in weekly intervals but can be switched to monthly (`-m`).
If there are sheets (or tabs) in the document you don't want to read in, you can skip them
with `-t`. In the spreadsheets, I also enter buy, sell and LEAPS orders, but I don't want
those to end up in the calculation in here, so you can skip "actions" that contain a certain
string with `-a`. Check my example spreadsheet linked above for the naming scheme I use.

In the end, you probably want to wrap the script with all your specific arguments into a
shell script or alias like so:

```bash
#!/bin/sh

BIN="/path/to/this/python/script.py"
SHEETS="/path/to/your/excel/sheet.xlsx"

$BIN -x $SHEETS -s "2021-05-03" \
    --skip_actions LEAPS buy sell \
    --skip_sheets blank Sheet3
```
