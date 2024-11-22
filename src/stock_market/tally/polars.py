from typing import Iterable


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


def sum_monthly(df, which: str):
    return df.sql(f"""
        select date, sum({which}), currency
        from self
        group by
            substr(date, 0, 8),
            currency
        order by 1, currency
    """)


def sum_quarterly(df, which: str):
    return df.sql(f"""
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


def sum_yearly(df, which: str):
    return df.sql(f"""
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


def sum_total(df, which: str):
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
