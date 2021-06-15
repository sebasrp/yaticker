import click

from yaticker import YaTicker


@click.command()
@click.option("--interval", default="5m", help="Interval/granularity of the data")
@click.option("--period", default="7d", help="Period you want to look back to")
@click.option(
    "--tickers", default="AMZN", help="comma separated list of symbols to watch"
)
def cli(tickers, period, interval):
    """Simple console client for yaticker"""
    data = YaTicker.get_tickers_data(
        tickers_string=tickers, period=period, interval=interval
    )
    print(data)


if __name__ == "__main__":
    cli()
