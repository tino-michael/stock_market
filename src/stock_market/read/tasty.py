from pathlib import Path
import polars as pl


def read_tasty_options_dir(path: Path):
    return _read_tasty_dir(path, function=read_tasty_options)


def read_tasty_dividends_dir(path: Path):
    return _read_tasty_dir(path, function=read_tasty_dividends)


def _read_tasty_dir(path: Path, function, pattern: str = "tasty_*"):
    return pl.concat(filter(lambda x: len(x), [
        function(f) for f in path.glob(pattern)
    ]))


def _read_tasty_file(path: Path, *filters):
    df = pl.read_csv(
        path,
        schema_overrides={
            "Date": pl.Datetime,
            "Strike Price": pl.String,
            "Value": pl.String,
            "Total": pl.String,
        }
    )
    df = df.with_columns(
        pl.col("Date").cast(pl.Date).cast(pl.String).alias("date"),
        pl.col("Root Symbol").alias("ticker"),
        pl.col("Currency").alias("currency"),
        pl.col("Total")
            .str.replace_all(",", "")
            .cast(pl.Float64).alias("credit"),
    ).filter(*filters)

    return df[["date", "ticker", "credit", "currency"]]


def read_tasty_options(path: Path):
    return _read_tasty_file(
        path,
        pl.col("Instrument Type") == "Equity Option"
    )

def read_tasty_dividends(path: Path):
    return _read_tasty_file(
        path,
        pl.col("Sub Type") == "Dividend",
        pl.col("credit") > 0
    )
