def skip_actions(df, actions):
    """
    Removes rows from the data frame where the "Action" entry starts with anything given by the
    `actions` list.
    """

    for skip in actions:
        df = df[df.loc[:, "Action"].str.startswith(skip)==False]

    return df


def get_owned_shares(
        df,
        buy_actions=["buy"], sell_actions=["sell"],
        action_column="Action", n_shares_column="Shares"):
    """
    Returns the number of shares owned from the given data frame.
    The strings in `buy_actions` and `sell_actions` are search for in the `action_column` and 
    define which entries are to be considered as shares bought and sold.
    """

    bought = sum(df[df.loc[:, action_column].str.startswith(a)].loc[:, n_shares_column].sum() for a in buy_actions)
    sold = sum(df[df.loc[:, action_column].str.startswith(a)].loc[:, n_shares_column].sum() for a in sell_actions)

    return bought - sold
