from ..tally_table import get_tally_table

import pandas as pd

def test_import():
    """
    Test some basic behaviour of the tally table function
    """

    interval = "weekly"
    start_date = None
    end_date = None

    data = [
        ["2021-10-30", +100],
        ["2021-10-31", -100],
        ["2021-10-20", +100]
    ]

    df = pd.DataFrame(
        data=data,
        columns=["Date", "Total Value"]
    )

    assert len(df) == 3
    assert df["Total Value"].sum() == 100

    tf = get_tally_table(df, interval, start_date, end_date)
    assert len(tf) == 2
    assert tf["Profit"].sum() == 100
    assert tf["Profit"][0] == 100
    assert tf["Profit"][1] == 0


def test_start_week():
    """
    Given a start date that is not a Monday, test that the periods in the tally table still start
    on Mondays.
    """
    interval = "weekly"
    start_date = None
    end_date = None

    data = [
        ["2021-10-30", 0],
        ["2021-10-28", 0],
        ["2021-10-31", 0]
    ]

    df = pd.DataFrame(
        data=data,
        columns=["Date", "Total Value"]
    )

    tf = get_tally_table(df, interval, start_date, end_date)

    idxs = tf.index
    assert idxs.min().start_time.dayofweek == 0
    assert idxs.min().end_time.dayofweek == 6
