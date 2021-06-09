import unittest

from yaticker.yaticker import YaTicker


class TestYaticker(unittest.TestCase):
    def test_init(self):
        yaticker = YaTicker()
        self.assertEqual(yaticker.tickers, "AMZN FB GGL")
        self.assertEqual(yaticker.fiatcurrency, "usd,eur")
        self.assertEqual(yaticker.period, "7d")
        self.assertEqual(yaticker.interval, "5m")


if __name__ == "__main__":
    unittest.main()
