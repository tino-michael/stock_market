import pandas as pd


def get_tally_table(df, interval, start_date=None, end_date=None, format=None):
    """
    Aggregates trade values from the input data frame `df` and puts them into a tally data frame.
    It sums up credits, debits and profits/losses within a time period given by `intervall`.
    Start and end date are either given or inferred from the earliest and latest date in `df`.
    """

    df["Date"] = pd.to_datetime(df['Date'], format=format)

    if start_date is None:
        start_date = df["Date"].min()
    if end_date is None:
        end_date = df["Date"].max()

    # get the frequency character for pandas ("quarterly" converts to "3 months")
    freq = interval[0].upper()
    if freq == "Q": freq = "3M"

    range = pd.period_range(start=start_date, end=end_date, freq=freq)

    tally_frame = pd.DataFrame(
        columns=["Debit", "Credit", "Profit"],
        index=range
    ).fillna(0)

    for idx, row in tally_frame.iterrows():
        pdf = df[df["Date"].between(idx.start_time, idx.end_time)]
        tv = pdf["Total Value"]
        credits = tv[tv < 0].sum()
        debits = tv[tv > 0].sum()

        row["Credit"] = credits
        row["Debit"] = debits
        row["Profit"] = debits + credits

    return tally_frame
