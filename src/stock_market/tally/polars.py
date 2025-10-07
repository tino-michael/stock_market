from typing import Iterable, Collection
import polars as pl


def filter_tickers(df, tickers: Iterable[str]):
    return df.sql(f"""
        select *
        from self
        where ticker in {tuple(tickers)}
    """)


def filter_dates(df, start_date: str, end_date: str):
    if start_date:
        df = df.sql(f"""
            select *
            from self
            where date(date) > date('{start_date}')
        """)

    if end_date:
        df = df.sql(f"""
            select *
            from self
            where date(date) <= date('{start_date}')
        """)

    return df


def filter_currencies(df, currencies: Collection[str] = []):
    df = df.sql(f"""
        select *
        from self
        where currency in {currencies}
    """.replace("[", "(").replace("]", ")"))

    return df


def skip_actions(df, actions: Collection[str]):
    for action in actions:
        df = df.sql(f"""
            select *
            from self
            where not action like '%{action}%'
        """)

    return df


def sum_monthly(df, which: str, yoy: bool = False, last: int = None):
    df = df.sql(f"""
        select date, sum({which}), currency
        from self
        group by
            substr(date, 0, 8),
            currency
        order by 1, currency
    """)

    if yoy:
        df = add_yoy_column(df, which, 12).sort(["date", "currency"])

    if last:
        sort_dates = sorted(df["date"].unique())
        last = min(last, len(sort_dates))
        first_date = sort_dates[-last]
        df = df.sql(f"""
            select * from self
            where date >= '{first_date}'
        """)

    return df


def sum_quarterly(df, which: str, yoy: bool = False, last: int = None):
    df = df.sql(f"""
        with grouping as (
            select *,
                date_part('year', date(date)) as year,
                date_part('quarter', date(date)) as quarter
            from self
        )
        select year, quarter, sum({which}), currency
        from grouping
        group by year, quarter, currency
        order by year, quarter, currency
    """)

    if yoy:
        df = add_yoy_column(df, which, 4).sort(["year", "quarter", "currency"])

    if last:
        sort_dates = df[["year", "quarter"]].unique().sql("""select * from self order by year, quarter""")
        last = min(last, len(sort_dates))
        (ye, qa) = sort_dates[-last]
        df = df.sql(f"""
            select * from self
            where concat(year, quarter) >= concat('{ye[0]}', '{qa[0]}')
        """)

    return df


def sum_yearly(df, which: str, yoy: bool = False, last: int = None):
    df = df.sql(f"""
        with grouping as (
            select *,
                date_part('year', date(date)) as year,
            from self
        )
        select year, sum({which}), currency
        from grouping
        group by year, currency
        order by year, currency
    """)

    if yoy:
        df = add_yoy_column(df, which, 1).sort(["year", "currency"])

    return df


def sum_total(df, which: str, yoy: bool = False):
    return df.sql(f"""
        with grouping as (
            select *,
                date_part('year', date(date)) as year,
            from self
        )
        select
            concat(min(year), '--', max(year)) as years,
            sum({which}), currency
        from grouping
        group by currency
        order by currency

    """)


def add_yoy_column(df: pl.DataFrame, which: str, shift: int):
    """
    Add a percentage gain year-over-year column to the dataframe.
    The gain is calculate relative to the value `shift` rows before;
    meaning shift=1 for yearly, =4 for quarterly, =12 for monthly tallies.
    The calculation is performed separately for each unique currency found in the frame.
    Resulting frames are concatenated again and so might still need sorting afterwards.
    """
    def _add_yoy(df):
        return df.with_columns((
                100 * (df[which] - df[which].shift(shift))/df[which].shift(shift)
            ).alias("YoY / %"))

    return pl.concat([
        _add_yoy(df.filter(pl.col("currency") == cur))
        for cur in df["currency"].unique()
    ])
