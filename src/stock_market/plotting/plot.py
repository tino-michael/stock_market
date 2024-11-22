import polars as pl
import seaborn as sb
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('qtagg')


def plot(df: pl.DataFrame, calc_yoy=False):
    df = df.with_columns(pl.sql_expr("CONCAT_WS('-', year, quarter) AS date"))

    df_total = df.sql("""
        select date, sum(dividends)
        from self
        group by date
        order by date
    """)

    ax = sb.barplot(
        data=df_total,
        x="date",
        y="dividends",
        label="EUR",
    )
    ax = sb.barplot(
        data=df.filter(pl.col("currency") == "USD"),
        x="date",
        y="dividends",
        label="USD",
    )

    plt.legend(title="currency")

    ax.tick_params(axis='x', rotation=45)
    ax.set_xlabel("Year - Quarter")

    if calc_yoy:
        yoy = []
        divs = df_total["dividends"]
        for i, row in enumerate(divs[4:]):
            yoy.append(row/divs[i])

        ax2 = ax.twinx()

        sb.lineplot(
            x=df_total["date"][4:],
            y=yoy,
            color="red",
            ax=ax2
        )

        ax2.set_ylabel("Year over Year change")
        ax2.yaxis.label.set_color('red')
        ax2.tick_params(axis='y', colors='red')
        ax2.set_ylim([0, None])

    plt.tight_layout()
    plt.show()
