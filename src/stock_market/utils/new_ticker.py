import os

CSV_HEADER_OPTIONS = "Action,Date,# Shares,Share Price,Status"


def new_ticker_options(ticker: str, target_dir: str):
    """
    Creates a new csv file for `ticker` in `target_dir` directory.
    The file is empty except for the `CSV_HEADER` as first and only line.

    The function catches `IOError` and exits with an error message.

    """
    full_path = os.path.join(target_dir, ticker.lower() + ".csv")

    if os.path.exists(full_path):
        print(f"File for {ticker=} already exists!")
        print("not overwriting")
        exit()

    try:
        with open(full_path, "w") as f:
            f.write(CSV_HEADER_OPTIONS)
        if os.path.exists(full_path):
            print(f"File for {ticker=} created successfully!")
    except IOError:
        print(f"Failed to create file for {ticker=}!")
        exit(-1)
