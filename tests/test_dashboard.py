import os
import pathlib
import unittest
from unittest.mock import patch

import yaml
from PIL import Image

from yaticker.dashboard import Dashboard
from yaticker.yaticker import YaTicker


class TestUtil(unittest.TestCase):
    TEST_CONFIG_NAME = "test_config.yaml"

    @classmethod
    def setUpClass(cls):
        cls.config_dict = {
            "watchlist": ["FOO", "BAR"],
            "cycle": False,
            "updatefrequency": 10,
            "showvolume": True,
            "period": "1y",
        }
        with open(cls.TEST_CONFIG_NAME, "w") as outfile:
            yaml.dump(cls.config_dict, outfile)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.TEST_CONFIG_NAME)

    @patch.object(Dashboard, "__abstractmethods__", set())
    def test_init(self):
        dashboard = Dashboard(width=200, height=100, dpi=100)
        self.assertEqual(200, dashboard.width)
        self.assertEqual(100, dashboard.height)
        self.assertEqual(100, dashboard.dpi)
        self.assertEqual(True, dashboard.cycle)
        self.assertEqual(300, dashboard.update_frequency)
        self.assertEqual(False, dashboard.show_volume)
        self.assertEqual("5d", dashboard.period)
        self.assertEqual(["AMZN", "FB", "APPL"], dashboard.watchlist)

    def test_load_config(self):
        expected_config = self.config_dict
        actual_config = Dashboard.load_config(self.TEST_CONFIG_NAME)
        self.assertDictEqual(expected_config, actual_config)

    def test_load_config_None(self):
        expected_config = {}
        actual_config = Dashboard.load_config(None)
        self.assertDictEqual(expected_config, actual_config)

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
