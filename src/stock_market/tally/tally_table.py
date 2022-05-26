import pandas as pd

from ..utils import utils


def get_tally_table(df, interval, start_date=None, end_date=None, format=None):
    """
    Aggregates trade values from the input data frame `df` and puts them into a tally data frame.
    It sums up credits, debits and profits/losses within a time period given by `interval`.
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

    date_range = pd.period_range(start=start_date, end=end_date, freq=freq)

    tally_frame = pd.DataFrame(
        columns=["Debit", "Credit", "Profit"],
        index=date_range
    ).fillna(0)

    for idx in tally_frame.index:
        pdf = df[df["Date"].between(idx.start_time, idx.end_time)]
        tv = pdf["Total Value"]
        credits = tv[tv < 0].sum()
        debits = tv[tv > 0].sum()

        tally_frame.loc[idx] = pd.Series(
            data=[credits, debits, credits+debits],
            index=["Credit", "Debit", "Profit"])

    return tally_frame


def get_acb_table(data_map):
    """
    Build the tally table for the adjusted cost basis per stock ticker.
    The table contains the number of shares held, the total profit/loss for this position,
    the "cashflow" as the profit disregarding buy and sell actions and the adjusted cost basis
    as the negative profit divided by the shares held (or zero when no shares held).
    The adj. cost basis is the effective cost paid for each held share considering all trading actions
    for this ticker symbol.
    """

    tally = {"Ticker": [], "Shares": [], "Profit": [], "Cashflow": [], "Adj. Cost Basis": []}

    for ticker, t_data in data_map.items():
        shares = utils.get_owned_shares(t_data)
        profit = t_data["Total Value"].sum()
        cashflow = utils.skip_actions(t_data, ["buy", "sell"])["Total Value"].sum()

        tally["Ticker"].append(ticker)
        tally["Shares"].append(shares)
        tally["Profit"].append(profit)
        tally["Cashflow"].append(cashflow)
        tally["Adj. Cost Basis"].append(-profit / shares if (shares > 0 and profit < 0) else 0)

    tickers = tally.pop("Ticker")
    df = pd.DataFrame(tally, index=tickers)

    pd.set_option('precision',2)
    return df



def get_dividend_tally(df, interval, start_date=None, end_date=None, format=None):
    """
    Start and end date are either given or inferred from the earliest and latest date in `df`.
    """

    df["Pay Date"] = pd.to_datetime(df["Pay Date"], format=format)

    if start_date is None:
        start_date = df["Pay Date"].min()
    if end_date is None:
        end_date = df["Pay Date"].max()

    # get the frequency character for pandas ("quarterly" converts to "3 months")
    freq = interval[0].upper()
    if freq == "Q": freq = "3M"

    range = pd.period_range(start=start_date, end=end_date, freq=freq)

    tally_frame = pd.DataFrame(
        columns=["Dividends"],
        index=range
    ).fillna(0)

    for idx, row in tally_frame.iterrows():
        pdf = df[df["Pay Date"].between(idx.start_time, idx.end_time)]
        row["Dividends"] = pdf["Total"].sum()

    return tally_frame
