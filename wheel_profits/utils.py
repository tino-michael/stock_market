def skip_actions(df, actions):
    """
    Removes rows from the data frame where the "Action" entry starts with anything given by the
    `actions` list.
    """

    for skip in actions:
        df = df[df.loc[:, "Action"].str.startswith(skip)==False]

    return df
