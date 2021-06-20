import pathlib
import unittest

from PIL import Image

from yaticker.dashboard import Dashboard
from yaticker.yaticker import YaTicker


class TestUtil(unittest.TestCase):
    def test_stock_graph_resolution(self):
        data = YaTicker.get_ticker_data(ticker="amc", period="5d", interval="1h")
        stock_image = Image.open(
            Dashboard.stock_graph(data, filename="test_candle.png")
        )
        width, height = stock_image.size
        print(f"directory: {pathlib.Path().absolute()}")
        self.assertAlmostEqual(264, width, delta=1)
        self.assertAlmostEqual(116, height, delta=1)


if __name__ == "__main__":
    unittest.main()
