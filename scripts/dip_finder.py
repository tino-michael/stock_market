#!/usr/bin/env python

import argparse

import yfinance as yf
import seaborn as sb
import matplotlib.pyplot as plt

from stock_market.financial import metrics as fm


metrics = {
    "sig": fm.calculate_bollinger_sig,
    "ma": fm.calculate_ma_deviation,
    "rsi": fm.calculate_rsi,
}

plot_labels = {
    "sig": "Bollinger Significance",
    "ma": "rel. %-Deviation from 100d Average",
    "rsi": "Relative Strength Index",
}

ap = argparse.ArgumentParser()

ap.add_argument("-t", "--tickers", nargs='*', type=str, required=True)
ap.add_argument("-o", "--vertical", type=str, default="sig", choices=metrics.keys())
ap.add_argument("-a", "--horizontal", type=str, default=None, choices=metrics.keys())

args = vars(ap.parse_args())


def plot_metrics_1d(calced, verti):
    calced = calced[verti].sort_values()
    sb.barplot(y=calced, x=calced.keys(), color="darkred")
    plt.gca().tick_params('x', rotation=45)
    plt.gca().set_xlabel(None)
    plt.gca().set_ylabel(plot_labels[verti])
    plt.gca().grid(axis="y")
    plt.tight_layout()
    plt.show()


def plot_metrics_2d(calced, verti, hori):
    pass


def main():
    data = yf.download(tickers=args["tickers"], period="6mo", interval="1d")["Close"]
    hori, verti = args["horizontal"], args["vertical"]
    calced = {o: metrics[o](data) for o in [hori, verti] if o}

    if verti == hori or hori is None:
        plot_metrics_1d(calced, verti=verti)
    else:
        plot_metrics_2d(calced, verti=verti, hori=hori)


if __name__ == "__main__":
    main()
