from pathlib import Path

import polars as pl


def read_options_dir(path: Path):
    csv = read_options_csv_dir(path)
    ibkr = read_options_ibkr_dir(path)

    if csv is not None and ibkr is not None:
        return pl.concat([csv, ibkr])
    if ibkr is not None:
        return ibkr
    if csv is not None:
        return csv


def read_options_csv_dir(path: Path, pattern: str = "[a-z]*.csv"):
    options_files = path.glob(pattern)

    try:
        options_df = pl.concat([
            read_options_csv(f)
            for f in options_files
        ])
        return options_df
    except:
        return None


def read_options_csv(path: Path):
    ticker = path.stem.upper()

    currency = "USD"
    if ticker in ["TKA", "SHA"]:
        currency = "EUR"
    try:
        df = (
            pl.read_csv(
                path,
                infer_schema=False
            )
            .rename(str.strip)
            .rename(str.lower)
            .sql(f"""
                select
                    action,
                    '{ticker}' as ticker,
                    '{currency}' as currency,
                    trim(date),
                    trim("# shares")::int4 * trim("share price")::float4 as profit,
                    status
                from self where date is not null
            """)
        )
    except:
        print(f"error loading file: {path}")
        exit(-1)

    return df

def read_options_ibkr_dir(path: Path, pattern: str = "IBKR_*"):
    option_files = path.glob(pattern)

    option_df = pl.concat([
        read_ibkr_csv(f)
        for f in option_files
    ])

    return option_df

def read_ibkr_csv(path: Path):
    opt_dict = {
        "action": [],
        "ticker": [],
        "currency": [],
        "date": [],
        "ticker": [],
        "profit": [],
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

            opt_dict["action"].append("")
            opt_dict["status"].append("")
            opt_dict["ticker"].append(ticker)
            opt_dict["currency"].append(currency)
            opt_dict["date"].append(date)
            opt_dict["profit"].append(profit)

    df = pl.DataFrame(opt_dict)
    df = df.with_columns(
        pl.col("profit").cast(pl.Float64)
    )
    return df
