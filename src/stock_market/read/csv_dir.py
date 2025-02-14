import os
import pandas as pd


def read_csv_file_wheel(filepath):
    """
    Reads a single csv file and imports its data into a pandas data frame.
    "Number of shares" and "Share Price" columns are consolidated into a "Total Value" column.
    """
    read_data = pd.read_csv(filepath, skip_blank_lines=True)\
        .rename(columns=lambda x: x.strip())
    read_data = read_data[read_data["Date"].notna()]

    try:
        col_action = read_data.loc[:, "Action"].str.strip()
        col_date = read_data.loc[:, "Date"].str.strip()
        col_value = read_data.loc[:, "# Shares"] * read_data.loc[:, "Share Price"]
        col_shares = read_data.loc[:, "# Shares"]
        col_status = read_data.loc[:, "Status"].str.strip()
    except KeyError:
        print("KeyError in file {}".format(filepath.split('/')[-1]))
        print("formatting error?")
        exit(0)

    ret_data = pd.DataFrame(
        data={
            "Action": col_action,
            "Date": col_date,
            "Total Value": col_value,
            "# Shares": col_shares,
            "Status": col_status})

    return ret_data


def read_csv_dir_wheel(dirpath, tickers=None):
    """
    Reads all csv files in the given directory and imports their data into a map of pandas
    data frames. If `tickers` is given, only consider files with basenames in that list.
    """

    data_dict = {}
    tickers = [x.upper() for x in tickers]

    for file_name in os.listdir(dirpath):
        if not file_name.endswith('csv'):
            continue

        ticker = os.path.splitext(file_name)[0].upper()

        if tickers and ticker not in tickers:
            continue

        df = read_csv_file_wheel(os.path.join(dirpath, file_name))

        data_dict[ticker] = df

    return data_dict


def read_csv_file_div(filepath):
    """
    Reads a single csv file and imports its data into a pandas data frame.
    "Number of shares" and "Share Price" columns are consolidated into a "Total Value" column.
    """
    read_data = pd.read_csv(filepath, skip_blank_lines=True).rename(columns=lambda x: x.strip())

    try:
        col_pay_date = read_data.loc[:, "Pay Date"]
        col_per_share = read_data.loc[:, "Div per Share"]
        col_total = read_data.loc[:, "Div Total"]
    except KeyError:
        print("KeyError in file {}".format(filepath.split('/')[-1]))
        print("formatting error?")
        exit(0)

    ret_data = pd.DataFrame(
        data={
            "Pay Date": col_pay_date,
            "Per Share": col_per_share,
            "Total": col_total})

    return ret_data


def read_csv_dir_div(dirpath, tickers=None):
    """
    Reads all csv files in the given directory and imports their data into a map of pandas
    data frames. If `tickers` is given, only consider files with basenames in that list.
    """

    data_dict = {}
    tickers = [x.upper() for x in tickers]

    for file_name in os.listdir(dirpath):
        if not file_name.endswith('csv'):
            continue

        ticker = os.path.splitext(file_name)[0].upper()

        if tickers and ticker not in tickers:
            continue

        df = read_csv_file_div(os.path.join(dirpath, file_name))

        data_dict[ticker] = df

    return data_dict
