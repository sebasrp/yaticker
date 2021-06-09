import click

from yaticker import YaTicker


@click.command()
@click.option("--tickers", default="AMZN", help="tickers to download data from")
def cli(tickers):
    """Simple console client for yaticker"""
    data = YaTicker.get_tickers_data(tickers_string=tickers)
    print(data)


if __name__ == "__main__":
    cli()
