def skip_actions(df, actions, action_column="Action"):
    """
    Removes rows from the data frame where the "Action" entry starts with anything given by the
    `actions` list.
    """

    for skip in actions:
        df = df[df.loc[:, action_column].str.contains(skip) == False]

    return df


def get_owned_shares(
        df,
        buy_actions=["buy"], sell_actions=["sell"],
        action_column="Action", n_shares_column="# Shares"):
    """
    Returns the number of shares owned from the given data frame.
    The strings in `buy_actions` and `sell_actions` are searched for in the `action_column` and
    define which entries are to be considered as shares bought and sold.
    """

    bought = sum(df[df.loc[:, action_column].str.contains(a)].loc[:, n_shares_column].sum() for a in buy_actions)
    sold = sum(df[df.loc[:, action_column].str.contains(a)].loc[:, n_shares_column].sum() for a in sell_actions)

    return bought - sold
