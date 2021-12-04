from howitzer.util.stats import *

import unittest


class TestFoltillaStats(unittest.TestCase):
    def setUp(self):
        self.test_list = [-5, 1, 8, 7, 2]

    def test_average(self):
        self.assertEqual(average(self.test_list), 2.6, "average is incorrect")

    def test_stddev(self):
        self.assertAlmostEqual(stddev(self.test_list),
                               4.6733, 4, "average is incorrect")

    def test_zscore(self):
        self.assertAlmostEqual(zscore(-5, 2.6, 4.6733), -
                               1.6263, 4, "zscore is incorrect")

    def test_corolation(self):
        x = [1, 3, 4, 5, 7]
        y = [5, 9, 7, 1, 13]
        self.assertAlmostEqual(corolation(x, y), 0.4, 1,
                               "corolation is incorrect")
