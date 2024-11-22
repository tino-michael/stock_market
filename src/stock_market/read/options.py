from pathlib import Path
from typing import Iterable

import polars as pl


def read_options_dir(path: Path, pattern: str = "*.csv"):
    options_files = path.glob(pattern)

    options_df = pl.concat([
        read_options_csv(f)
        for f in options_files
    ])

    return options_df


def read_options_csv(path: Path):
    ticker = path.stem.upper()

    currency = "USD"
    if ticker in ["TKA", "SHA"]:
        currency = "EUR"

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

    return df


def skip_actions(df, actions: Iterable[str]):
    for action in actions:
        df = df.sql(f"""
            select *
            from self
            where not action like '%{action}%'
        """)

    return df
