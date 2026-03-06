# Stock Market

A collection of scripts and tools for tracking stock market investments, including dividend income and options trading (such as the "Wheel" strategy).

## Overview

The main script, `scripts/tally.py`, provides a powerful command-line tool for aggregating and analyzing your investment income. It supports:

- **Dividend tracking** - Monitor dividend income from your stock holdings
- **Options trading tracking** - Track profits and losses from options trades (including the "Wheel" strategy)
- **Combined tracking** - Analyze both dividends and options income together

The script can import data from multiple sources:
- **Interactive Brokers (IBKR)** export files
- **Tastytrade** export files
- Custom CSV files

## Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install .
```

## Quick Start

### Create a new options tracking file

```bash
# Creates 'aapl.csv' in the specified directory with proper headers
uv run scripts/tally.py --new AAPL --csv-directory /path/to/csv/files
```

### Track dividends only

```bash
# Read IBKR dividend reports
uv run scripts/tally.py --dividends --ibkr-directory /path/to/ibkr/reports

# Read Tastytrade dividend reports
uv run scripts/tally.py --dividends --tasty-directory /path/to/tasty/reports

# Read from both sources
uv run scripts/tally.py --dividends --ibkr-directory /path/to/ibkr --tasty-directory /path/to/tasty
```

### Track options only

```bash
# Read IBKR options reports
uv run scripts/tally.py --options --ibkr-directory /path/to/ibkr/reports

# Read Tastytrade options reports
uv run scripts/tally.py --options --tasty-directory /path/to/tasty/reports

# Read from both sources
uv run scripts/tally.py --options --ibkr-directory /path/to/ibkr --tasty-directory /path/to/tasty
```

### Track both dividends and options

```bash
# Combined view of all income
uv run scripts/tally.py --dividends --options --ibkr-directory /path/to/ibkr --tasty-directory /path/to/tasty
```

## Command-Line Options

### Data Source Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dividends` | `--div` | Include dividend data |
| `--options` | `--opt` | Include options data |
| `--csv-directory` | - | Directory containing custom CSV files |
| `--ibkr-directory` | - | Directory containing IBKR export files (pattern: `IBKR_*`) |
| `--tasty-directory` | - | Directory containing Tastytrade export files (pattern: `tasty_*`) |

**Note:** CSV files for custom options tracking should have the following header:
```csv
Action,Date,# Shares,Share Price,Status
```

### Filtering Options

| Option | Short | Description |
|--------|-------|-------------|
| `--tickers` | `-t` | Filter by ticker symbols (comma-separated) |
| `--currencies` | `-c` | Filter by currencies (comma-separated) |
| `--start-date` | `-s` | Start date (YYYY-MM-DD format) |
| `--end-date` | `-e` | End date (YYYY-MM-DD format) |

### Aggregation Period Options

| Option | Short | Description |
|--------|-------|-------------|
| `--daily` | `-d` | Show daily totals |
| `--monthly` | `-m` | Show monthly totals (default) |
| `--quarterly` | `-q` | Show quarterly totals |
| `--yearly` | `-y` | Show yearly totals |
| `--total` | - | Show overall totals (always shown) |

**Note:** Only one period option can be used at a time.

### Display Options

| Option | Description |
|--------|-------------|
| `--table-yoy` | Include year-over-year percentage in table |
| `--no-bar` | Disable visual progress bars in output |
| `--last N` | Show only the last N periods |

### Plotting Options

| Option | Short | Description |
|--------|-------|-------------|
| `--plot` | `-p` | Show a bar plot of the data |
| `--plot-yoy` | - | Include year-over-year calculation in plot |

### Other Options

| Option | Description |
|--------|-------------|
| `--new TICKER` | Create a new CSV template file for tracking TICKER |
| `--skip-actions` | Skip actions starting with specified strings |


## Output Format

The script outputs tables with the following structure (example for quarterly output):

```
┌──────┬─────────┬───────────┬───────────┐
│ year ┆ quarter ┆ credit    ┆ currency  │
╞══════╪═════════╪═══════════╪═══════════╡
│ 2023 ┆ 1       ┆ 1250.50   ┆ USD       │
│ 2023 ┆ 2       ┆ 1450.75   ┆ USD       │
│ 2023 ┆ 3       ┆ 1100.25   ┆ USD       │
│ 2023 ┆ 4       ┆ 1800.00   ┆ USD       │
│ 2024 ┆ 1       ┆ 1300.50   ┆ USD       │
│ 2024 ┆ 2       ┆ 1550.75   ┆ USD       │
└──────┴─────────┴───────────┴───────────┘
```

With `--table-yoy`, an additional column shows percentage change from the corresponding period in the previous year.

With `--bar`, a visual progress bar column is added showing relative magnitude of each value.

## Data Formats

### IBKR CSV Format

IBKR activity statement export using at least "Combined Dividends" and "Trades" sections.
The script expects:
- Options data in rows containing "Equity and Index Options"
- Dividend data in rows where the first column is "Dividends"

### Tastytrade CSV Format

Tastytrade transaction history export:
- Options: rows where "Instrument Type" = "Equity Option"
- Dividends: rows where "Sub Type" = "Dividend"

### Custom CSV Format

For manual tracking, create CSV files with this header:
```csv
Action,Date,# Shares,Share Price,Status
```

**Important**: You must distinguish between debits and credits:
- **Credits** (money received): Use positive values
  - Example: Selling an option: 100 shares, premium of $2.50/share → `100` in "# Shares", `2.50` in "Share Price"
- **Debits** (money spent): Use negative values
  - Example: Buying back an option: 100 shares, cost of $0.50/share → `100` in "# Shares", `-0.50` in "Share Price"

## Tips and Best Practices

1. **Organize your files**: Keep IBKR and Tastytrade exports in separate directories
2. **Use period filtering**: Default aggregation is monthly; use `--quarterly` or `--yearly` for longer-term views
3. **Filter by ticker**: Focus on specific holdings using `--tickers`
4. **Track currencies separately**: Use `--currencies` if you hold positions in multiple currencies
5. **Visualize trends**: Use `--plot` or `--table-yoy` to see growth patterns
6. **Date ranges**: Combine `--start-date` and `--end-date` to analyze specific periods
7. **Create templates**: Use `--new` to quickly create new tracking files

## Dependencies

- Python >= 3.13
- polars >= 1.34.0
- loguru >= 0.7.3
- pydantic-settings >= 2.12.0
- pyqt6 >= 6.9.1 (for plotting)
- seaborn >= 0.13.2 (for plotting)

## License

See [LICENSE](LICENSE) file for details.
