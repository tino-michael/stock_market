import sys
import pandas as pd


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
    sys.exit(0)
