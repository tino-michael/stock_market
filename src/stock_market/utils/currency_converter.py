"""
Currency conversion for stock market tally data.

Fetches live exchange rates from the Frankfurter API
(https://www.frankfurter.app) – no API key required, backed by
European Central Bank data, supports ~30 currencies.

Rates are cached in memory for the duration of the script run.
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from pathlib import Path
from typing import Dict

import polars as pl

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Frankfurter API endpoint (no key needed, ECB-sourced rates)
FRANKFURTER_URL = "https://api.frankfurter.app/latest?from={base}"

# How long (in seconds) to keep cached rates before re-fetching
CACHE_TTL = 3600  # 1 hour

# Optional: persistent cache file so repeated runs on the same day
# avoid the network call entirely
CACHE_FILE = Path(
    os.environ.get(
        "STOCK_MARKET_CURRENCY_CACHE",
        str(Path.home() / ".cache" / "stock_market_rates.json"),
    )
)

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------
_rates_cache: Dict[str, tuple[float, Dict[str, float]]] = {}
"""Maps base_currency -> (timestamp, {target: rate})"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def convert_dataframe(df: pl.DataFrame, target_currency: str) -> pl.DataFrame:
    """
    Convert all monetary values in *df* from their original currencies
    to *target_currency* using live exchange rates.

    Parameters
    ----------
    df : pl.DataFrame
        Must contain columns ``"credit"`` (float) and ``"currency"`` (str).
    target_currency : str
        Three-letter ISO currency code (e.g. ``"EUR"``, ``"USD"``, ``"CHF"``).

    Returns
    -------
    pl.DataFrame
        A new DataFrame with ``credit`` converted to *target_currency*
        and all rows having ``currency == target_currency``.
    """
    target = target_currency.upper()

    # Collect distinct source currencies present in the data
    source_currencies: set[str] = set(df["currency"].unique().to_list())
    if not source_currencies:
        logger.warning("No currencies found in data – nothing to convert.")
        return df

    # If everything is already in the target currency, no work needed
    if source_currencies == {target}:
        logger.info("All values already in %s – no conversion needed.", target)
        return df

    logger.info(
        "Converting currencies %s → %s",
        sorted(source_currencies),
        target,
    )

    # Fetch all rates relative to USD once, then compute cross-rates.
    # This is more efficient than one API call per source currency.
    usd_rates = _fetch_rates("USD")

    def conversion_factor(source: str) -> float:
        """Return multiplier to convert *source* -> *target*."""
        if source == target:
            return 1.0
        if source == "USD":
            return usd_rates.get(target, 1.0)
        if target == "USD":
            return 1.0 / usd_rates.get(source, 1.0)
        # Cross-rate via USD
        rate_src_to_usd = usd_rates.get(source)
        rate_usd_to_tgt = usd_rates.get(target)
        if rate_src_to_usd is None or rate_usd_to_tgt is None:
            logger.warning(
                "Missing rate for %s or %s – treating as 1.0 (no conversion).",
                source,
                target,
            )
            return 1.0
        return rate_usd_to_tgt / rate_src_to_usd

    # Build a mapping column for the conversion factor
    factor_map: dict[str, float] = {
        src: conversion_factor(src) for src in source_currencies
    }

    # Apply conversion: credit *= factor, currency = target
    df = df.with_columns(
        (pl.col("credit") * pl.col("currency").replace_strict(factor_map)).alias(
            "credit"
        ),
        pl.lit(target).alias("currency"),
    )

    logger.info("Conversion to %s complete.", target)
    return df


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fetch_rates(base: str) -> Dict[str, float]:
    """
    Return a dict mapping target currency -> rate for the given *base*
    currency.  Results are cached in memory (and optionally on disk).
    """
    now = time.time()
    # Check in-memory cache
    cached = _rates_cache.get(base)
    if cached is not None and (now - cached[0]) < CACHE_TTL:
        return cached[1]

    # Check persistent cache file
    disk_rates = _load_disk_cache()
    if disk_rates.get("base") == base:
        cache_time = disk_rates.get("_cached_at", 0)
        if (now - cache_time) < CACHE_TTL:
            _rates_cache[base] = (now, disk_rates.get("rates", {}))
            return disk_rates.get("rates", {})

    # Fetch from API
    url = FRANKFURTER_URL.format(base=base)
    logger.info("Fetching exchange rates from %s", url)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "stock-market/0.1"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.error("Failed to fetch exchange rates: %s", exc)
        # Fall back to a minimal built-in snapshot (common pairs)
        logger.warning("Falling back to hardcoded rate snapshot.")
        data = _fallback_rates(base)

    rates: Dict[str, float] = data.get("rates", {})
    # Also inject the base currency itself (rate=1.0)
    rates[base] = 1.0

    # Update caches
    _rates_cache[base] = (now, rates)
    _save_disk_cache({"base": base, "rates": rates, "_cached_at": now})

    return rates


def _load_disk_cache() -> dict:
    """Load persistent rate cache from disk, or return empty dict."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.debug("Could not load disk cache: %s", exc)
    return {}


def _save_disk_cache(data: dict) -> None:
    """Persist rate cache to disk."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    except OSError as exc:
        logger.debug("Could not save disk cache: %s", exc)


# ---------------------------------------------------------------------------
# Fallback rates (hardcoded snapshot)
# ---------------------------------------------------------------------------

_FALLBACK_RATES: dict[str, dict[str, float]] = {
    "USD": {
        "USD": 1.0,
        "EUR": 0.88168,
        "GBP": 0.75986,
        "CHF": 0.81317,
        "JPY": 161.85,
        "CAD": 1.424,
        "AUD": 1.4507,
        "NZD": 1.7735,
        "SEK": 9.7593,
        "NOK": 9.8902,
        "DKK": 6.5901,
        "PLN": 3.7802,
        "CZK": 21.383,
        "HUF": 313.46,
        "CNY": 6.7982,
        "HKD": 7.8406,
        "SGD": 1.2977,
        "INR": 94.39,
        "MXN": 17.6389,
        "ZAR": 16.5615,
        "BRL": 5.2019,
        "KRW": 1542.92,
        "ILS": 2.9759,
        "ISK": 126.96,
        "IDR": 17982.0,
        "MYR": 4.1175,
        "PHP": 61.184,
        "RON": 4.6128,
        "THB": 33.4,
        "TRY": 46.515,
    },
}


def _fallback_rates(base: str) -> dict:
    """
    Return a fallback rates structure (matching Frankfurter's JSON shape)
    when the live API is unreachable.

    Only contains the ~20 most common currencies against USD.
    Cross-rates against other bases are computed on the fly.
    """
    usd_rates = _FALLBACK_RATES.get("USD", {})
    if base == "USD":
        return {"amount": 1.0, "base": "USD", "date": "1970-01-01", "rates": usd_rates}

    base_to_usd = usd_rates.get(base, 1.0)
    computed = {}
    for currency, rate_vs_usd in usd_rates.items():
        computed[currency] = rate_vs_usd / base_to_usd
    computed[base] = 1.0
    return {"amount": 1.0, "base": base, "date": "1970-01-01", "rates": computed}
