import configparser
import os

import yfinance as yf


class YaTicker(object):
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = YaTicker.create_default_config()

        config = configparser.ConfigParser()
        config.read(config_file)
        self.tickers = config["default"]["tickers"]
        self.fiatcurrency = config["default"]["fiatcurrency"]
        self.period = config["default"]["period"]
        self.interval = config["default"]["interval"]
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

    @staticmethod
    def create_default_config():
        config = configparser.ConfigParser()
        config["default"] = {
            "tickers": "AMZN FB GGL",
            "fiatcurrency": "usd,eur",
            "period": "7d",
            "interval": "5m",
        }
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.ini"
        )
        with open(file_path, "w") as configfile:
            config.write(configfile)
        return file_path
