from pathlib import Path

import polars as pl


def read_ibkr_directory(path: Path, pattern: str = "IBRK_*"):

    divi_files = path.glob(pattern)

    divi_df = pl.concat([
        read_ibkr_csv(f)
        for f in divi_files
    ])

    return divi_df


def read_ibkr_csv_2(path: Path):
    """
    This is not faster and less robust compared to the other version.
    This needs the exported csv files to be pre-processed to have superfluous rows removed by hand.
    (i.e. rows that are too short and make `read_csv` fail)
    """
    df = (
        pl.read_csv(path)
        .rename(str.strip)
        .rename(str.lower)
        .sql(r"""
            select
                currency,
                date,
                substr(description, 0, strpos(description, '\(')) as ticker,
                amount as dividends
             from self
             where header not like '%Total%'
        """)
    )

    return df


def read_ibkr_csv(path: Path):
    divi_dict = {
        "currency": [],
        "date": [],
        "ticker": [],
        "dividends": [],
    }

    with open(path, "r") as f:
        for line in f:
            row = line.split(",")

            if row[0] != "Dividends":
                continue

            if row[1] == "Header":
                continue

            if "Total" in row[2]:
                continue

            divi_dict["currency"].append(row[2])
            divi_dict["date"].append(row[3])
            divi_dict["ticker"].append(row[4].split('(')[0].strip())
            divi_dict["dividends"].append(row[5].strip())

    df = pl.DataFrame(divi_dict)
    df = df.with_columns(
        pl.col("dividends").cast(pl.Float64)
    )

    return df
