from stock_market.utils import get_owned_shares

import pandas as pd


def test_owened_shares_buy():

    data = [
        ["buy", 100],
        ["buy", 100],
    ]

    df = pd.DataFrame(
        data=data,
        columns=["Action", "# Shares"]
    )

    shares = get_owned_shares(df)
    assert shares == 200


def test_owened_shares_buy_sell():

    data = [
        ["buy", 100],
        ["buy", 100],
        ["sell", 100]
    ]

    df = pd.DataFrame(
        data=data,
        columns=["Action", "# Shares"]
    )

    shares = get_owned_shares(df)
    assert shares == 100


def test_owened_shares_buy_sell_out():

    data = [
        ["buy", 100],
        ["sell", 100],
        ["buy", 100],
        ["sell", 100]
    ]

    df = pd.DataFrame(
        data=data,
        columns=["Action", "# Shares"]
    )

    shares = get_owned_shares(df)
    assert shares == 0
