#!/usr/bin/env python

import pandas as pd
import datetime as dt
import dateutil.relativedelta as rd

import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-x", "--excel_sheet", type=str, default=None)
ap.add_argument("-s", "--start_date", type=str, required=True)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-f", "--date_format", type=str, default="%Y-%m-%d")
ap.add_argument("-m", "--monthly", default=False, action='store_true')
ap.add_argument("-a", "--skip_actions", nargs='*', type=str)
ap.add_argument("-t", "--skip_sheets", nargs='*', type=str)

args = vars(ap.parse_args())

# small class to collect credits and debits and have a nice string representation
class CreditDebit:
    def __init__(self):
        self.c = 0
        self.d = 0
    def sum(self):
        return self.c - self.d
    def __repr__(self):
        return f"p: {self.c}, l: {self.d}, total: {self.sum()}"

class DateRange:
    def __init__(self, start, end, inclusive=False):
        self.start = start
        self.end = end
        if not inclusive:
            self.end += dt.timedelta(days=-1)
    def contains(self, date):
            return self.start <= date <= self.end
    def __repr__(self):
        return \
            f"{self.start.strftime(args['date_format'])}" \
            + " to " + \
            f"{self.end.strftime(args['date_format'])}"


start_date = dt.datetime.strptime(args["start_date"], args["date_format"])
time_delta = dt.timedelta(days=7) if not args["monthly"] else rd.relativedelta(months=+1)
last_date = dt.datetime.today() if args["end_date"] is None else dt.datetime.strptime(args["end_date"], args["date_format"])

weekly_p_l = dict()
while (start_date + time_delta < last_date):
    weekly_p_l[DateRange(start_date, start_date + time_delta)] = CreditDebit()
    start_date += time_delta

weekly_p_l[DateRange(start_date, last_date, True)] = CreditDebit()


# I'm only interested in regular cashflow actions. "buy" and "sell" refers to the underlying
# stocks and means the options got assigned. LEAPS are long-term investments and ought not
# to show up here either.
skip_actions = args["skip_actions"] or []

# The document contains some more sheets (template and book keeping) that don't belong
# into the weekly tally
skip_sheets = args["skip_sheets"] or []

# read in the excel spreadsheets document
workbook = args["sheet"]
all_frames = pd.read_excel(workbook, sheet_name=None)

for key, df in all_frames.items():

    # skip sheets that do not contain wheel data
    if key in skip_sheets:
        continue

    # - split debit and credit columns
    # - empty cells are read as NaN, drop those
    df_p, df_l = \
        df.iloc[2:, [0,1,4]].dropna(), \
        df.iloc[2:, [7,8,11]].dropna()

    # remove buy, sell and LEAPS actions
    for skip in skip_actions:
        df_p = df_p[df_p.iloc[:, 0].str.contains(skip)==False]
        df_l = df_l[df_l.iloc[:, 0].str.contains(skip)==False]

    for i, row in df_p.iterrows():
        date_obj = pd.to_datetime(row.iloc[1])
        for time, p_l in weekly_p_l.items():
            if time.contains(date_obj):
                p_l.c += row.iloc[2]
                break

    for i, row in df_l.iterrows():
        date_obj = pd.to_datetime(row.iloc[1])
        for time, p_l in weekly_p_l.items():
            if time.contains(date_obj):
                p_l.d += row.iloc[2]
                break

# remove empty entries
weekly_p_l = {i:j for i,j in weekly_p_l.items() if j != CreditDebit()}
for p in weekly_p_l.items():
    print(p)
