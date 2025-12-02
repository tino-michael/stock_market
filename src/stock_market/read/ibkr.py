from pathlib import Path

import polars as pl


def read_ibkr_options_dir(path: Path):
    return _read_ibkr_dir(path, function=read_ibkr_options)


def read_ibkr_dividends_dir(path: Path):
    return _read_ibkr_dir(path, function=read_ibkr_dividends)


def _read_ibkr_dir(path: Path, function, pattern: str = "IBKR_*"):
    return pl.concat(filter(lambda x: len(x), [
        function(f) for f in path.glob(pattern)
    ]))


def read_ibkr_options(path: Path):
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

            if "Equity and Index Options" not in row:
                continue
            if row[1] == "SubTotal" or row[1] == "Total":
                continue

            ticker = row[5].split(" ")[0]
            currency = row[4]
            date = row[6].strip('"')
            profit = row[10]

            if profit == "0":
                continue

            opt_dict["action"].append("")
            opt_dict["status"].append("")
            opt_dict["ticker"].append(ticker)
            opt_dict["currency"].append(currency)
            opt_dict["date"].append(date)
            opt_dict["credit"].append(profit)

    df = pl.DataFrame(opt_dict)
    df = df.with_columns(
        pl.col("credit").cast(pl.Float64)
    )
    return df


def read_ibkr_dividends(path: Path):
    divi_dict = {
        "currency": [],
        "date": [],
        "ticker": [],
        "credit": [],
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
            divi_dict["credit"].append(row[5].strip())

    df = pl.DataFrame(divi_dict)
    df = df.with_columns(
        pl.col("credit").cast(pl.Float64)
    )

    return df
