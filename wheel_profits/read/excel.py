"""
legacy excel sheet importing
"""

import pandas as pd

import datetime as dt
import dateutil.relativedelta as rd


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



def get_weekly_p_l(args):
    start_date = dt.datetime.strptime(args["start_date"], args["date_format"])
    time_delta = dt.timedelta(days=7) if not args["monthly"] else rd.relativedelta(months=+1)
    last_date = dt.datetime.today() if args["end_date"] is None \
            else dt.datetime.strptime(args["end_date"], args["date_format"])

    weekly_p_l = dict()
    while start_date + time_delta < last_date:
        weekly_p_l[DateRange(start_date, start_date + time_delta)] = CreditDebit()
        start_date += time_delta

    weekly_p_l[DateRange(start_date, last_date, True)] = CreditDebit()

    return weekly_p_l


def read_excel(sheet_path, weekly_p_l, skip_sheets=[], skip_actions=[]):
    all_frames = pd.read_excel(sheet_path, sheet_name=None)

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
    weekly_p_l = {i:j for i,j in weekly_p_l.items() if j.sum() != 0}
    total = 0
    for p in weekly_p_l.items():
        print(p)
        total += p[1].sum()

    print("total:", total)
