from pathlib import Path
from loguru import logger
import polars as pl

def read_tasty_options_dir(path: Path, pattern: str = "tasty_*"):
    options_files = path.glob(pattern)

    options_df = pl.concat([
        read_tasty_options(f)
        for f in options_files
    ])

    return options_df


def read_tasty_options(path: Path):
    opt_dict = {
        "action": [],
        "ticker": [],
        "currency": [],
        "date": [],
        "ticker": [],
        "credit": [],
        "status": [],
    }

    with open(path, "r") as f:
        for line in f:
            row = line.split(",")
            try:
                int(row[0])
            except ValueError:
                # it's probably the first row (i.e. the header)
                continue

            what = row[5].split()[0]
            if what not in ["PUT", "CALL"]:
                logger.debug(f"skipping type {what}")
                continue


            profit = row[28].strip('"').replace('$', '')

            opt_dict["action"].append("tasty")
            opt_dict["ticker"].append(row[4].split('-')[0])
            opt_dict["currency"].append("USD")
            opt_dict["date"].append(row[12])
            opt_dict["credit"].append(profit)
            opt_dict["status"].append("closed")

    df = pl.DataFrame(opt_dict)
    df = df.with_columns(
        pl.col("credit").cast(pl.Float64)
    )
    return df
