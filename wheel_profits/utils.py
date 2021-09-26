import pandas as pd


def skip_actions(df, actions):

    for skip in actions:
        df = df[df.iloc[:, 0].str.startswith(skip)==False]

    return df
