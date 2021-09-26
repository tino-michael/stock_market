import os
import pandas as pd

def read_csv_file(filepath):
    read_data = pd.read_csv(filepath, skip_blank_lines=True)

    try:
        col_date = read_data.loc[:, "Date"]
        col_value = read_data.loc[:, "# of Shares"] * read_data.loc[:, "Share Price"]
        col_status = read_data.loc[:, "Status"]
    except KeyError:
        print("KeyError in file {}".format(filepath.split('/')[-1]))
        print("formatting error?")
        exit(0)

    ret_data = pd.DataFrame(
        data={
            "Date": col_date,
            "Total Value": col_value,
            "Status": col_status})

    return ret_data

def read_csv_dir(dirpath):

    data_dict = {}

    for file_name in os.listdir(dirpath):
        if not file_name.endswith('csv'): continue

        ticker = os.path.splitext(file_name)[0].upper()
        df = read_csv_file(os.path.join(dirpath, file_name))

        data_dict[ticker] = df

    return data_dict
