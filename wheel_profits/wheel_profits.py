#!/usr/bin/env python

import pandas as pd
import datetime as dt
import dateutil.relativedelta as rd

import argparse

from read_csv_dir import read_csv_dir
ap = argparse.ArgumentParser()
ap.add_argument("-x", "--excel_sheet", type=str, default=None)
ap.add_argument("-d", "--csv_directory", type=str, default=None)
ap.add_argument("-s", "--start_date", type=str, required=True)
ap.add_argument("-e", "--end_date", type=str, default=None)
ap.add_argument("-f", "--date_format", type=str, default="%Y-%m-%d")
ap.add_argument("-m", "--monthly", default=False, action='store_true')
ap.add_argument("-a", "--skip_actions", nargs='*', type=str)
ap.add_argument("-t", "--skip_sheets", nargs='*', type=str)

args = vars(ap.parse_args())


class CreditDebit:
    """ small class to collect credits and debits and have a nice string representation
    """
    def __init__(self):
        self.c = 0
        self.d = 0

    def sum(self):
        """ return the differens between credits and debits, i.e. total gains
        """
        return self.c - self.d

    def __repr__(self):
        return f"p: {self.c}, l: {self.d}, total: {self.sum()}"


class DateRange:
    """ simple time interval that can check whether it contains another date
    """
    def __init__(self, start, end, inclusive=False):
        self.start = start
        self.end = end
        if not inclusive:
            self.end += dt.timedelta(days=-1)

    def contains(self, other):
        """ checks whether another date is contained within this range
        """
        return self.start <= other <= self.end

    def __repr__(self):
        return \
            f"{self.start.strftime(args['date_format'])}" \
            + " to " + \
            f"{self.end.strftime(args['date_format'])}"


start_date = dt.datetime.strptime(args["start_date"], args["date_format"])
time_delta = dt.timedelta(days=7) if not args["monthly"] else rd.relativedelta(months=+1)
last_date = dt.datetime.today() if args["end_date"] is None \
        else dt.datetime.strptime(args["end_date"], args["date_format"])

weekly_p_l = dict()
while start_date + time_delta < last_date:
    weekly_p_l[DateRange(start_date, start_date + time_delta)] = CreditDebit()
    start_date += time_delta

weekly_p_l[DateRange(start_date, last_date, True)] = CreditDebit()


if args["csv_directory"] is not None:
    data_map = read_csv_dir(args["csv_directory"])
elif args["excel_sheet"] is not None:
    from read_excel import read_excel
    # read in the excel spreadsheets document
    workbook = args["excel_sheet"]
    read_excel(workbook, weekly_p_l, args["skip_sheets"] or [], args["skip_actions"] or [])




for ticker, df in data_map.items():
    for _, row in df.iterrows():
        date = pd.to_datetime(row.loc["Date"])
        for time, p_l in weekly_p_l.items():
            if time.contains(date):
                value = row.loc["Total Value"]
                if value > 0:
                    p_l.c += value
                else:
                    p_l.d -= value
                break

# remove empty entries
weekly_p_l = {i:j for i,j in weekly_p_l.items() if j != CreditDebit()}
total = 0
for p in weekly_p_l.items():
    print(p)
    total += p[1].sum()
print("total:", total)
