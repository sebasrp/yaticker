import yfinance as yf
from bottle import request, route, run


class YaTicker(object):
    def __init__(self):
        return

    @staticmethod
    def get_tickers_data(
        tickers_string: str = "AMZN", period: str = "7d", interval: str = "5m"
    ):
        """Return the list of tickers data."""
        data = yf.download(
            tickers=tickers_string, period=period, interval=interval, group_by="ticker"
        )
        return data

    @staticmethod
    def get_ticker_data(ticker: str = "AMZN", period: str = "1d", interval: str = "1m"):
        """Return the ticker data."""
        ticker_data = yf.Ticker(ticker)
        data = ticker_data.history(period=period, interval=interval)
        return data

    @route("/ticker/<symbol>")
    def ticker(symbol="amzn"):
        period = request.query.get("period", default="1d")
        interval = request.query.get("interval", default="1m")
        data = YaTicker.get_ticker_data(ticker=symbol, interval=interval, period=period)
        data_json = data.to_json(orient="index")
        return data_json

    def run(self):
        run(host="localhost", port=8080, debug=True)


def main():
    yaticker = YaTicker()
    yaticker.run()


if __name__ == "__main__":
    main()
