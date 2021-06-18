import unittest

from util import util


class TestUtil(unittest.TestCase):
    def test_get_percentage_diff_equal(self):
        actual = util.get_percentage_diff(77, 77)
        expected = 0.0
        self.assertEqual(expected, actual)

    def test_get_percentage_diff_negative(self):
        actual = util.get_percentage_diff(100, 200)
        expected = -50
        self.assertEqual(expected, actual)

    def test_get_percentage_diff_positive(self):
        actual = util.get_percentage_diff(150, 100)
        expected = 50
        self.assertEqual(expected, actual)

    def test_get_percentage_diff_zero(self):
        actual = util.get_percentage_diff(100, 0)
        expected = float("inf")
        self.assertEqual(expected, actual)

    def test_number_to_string_big(self):
        actual = util.number_to_string(2000)
        self.assertEqual("2,000", actual)

    def test_number_to_string_small(self):
        actual = util.number_to_string(1.23456789)
        self.assertEqual("1.2346", actual)


if __name__ == "__main__":
    unittest.main()
