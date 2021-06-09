import yfinance as yf


class YaTicker(object):
    def __init__(self):
        return

    @staticmethod
    def get_tickers_data(
        tickers_string: str = "AMZN", period: str = "7d", interval: str = "5m"
    ):
        """Return the tickers data."""
        data = yf.download(
            tickers=tickers_string, period=period, interval=interval, group_by="ticker"
        )
        return data
