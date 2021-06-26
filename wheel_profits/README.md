# Wheel Profits

This script calculates your weekly / monthly profits and/or losses you produced with your
options trading. It reads in an excel spreadsheet where you put in all your trades, and
extracts and distils all your credits and debits.

## Background

This script was heavily inspired by the [In the Money](https://www.youtube.com/channel/UCfMiRVQJuTj3NpZZP1tKShQ)
YouTube channel. In one of his video tutorials, Adam presented the "Wheel" strategy for
stock options trading and provided a link to a convenient Google spreadsheet
([click here](https://docs.google.com/spreadsheets/d/1mUJYD9jdVeEl-dwTfq2aXiPINf8698OehsSe34xOUfc/edit?usp=sharing) for my version with updated formatting).
This spreadsheet can be exported and/or published (File -> Publish to the web) as an excel
document which then can be read by this here python script.

## Usage

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
