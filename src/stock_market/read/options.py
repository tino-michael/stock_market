from pathlib import Path

import polars as pl
raise DeprecationWarning



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
