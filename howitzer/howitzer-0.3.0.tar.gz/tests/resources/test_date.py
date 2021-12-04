from howitzer.util.date import *

from datetime import datetime, timezone
import unittest


class TestFoltillaDateStrings(unittest.TestCase):
    def setUp(this):
        this.test_date = datetime(2021, 1, 1)

    def test_shortStringFormat(this):
        this.assertEqual(shortStringFormat(this.test_date), "1Jan2021")

    def test_shortMonthString_Jan(this):
        this.assertEqual(shortMonthString(1), "Jan")

    def test_shortMonthString_Feb(this):
        this.assertEqual(shortMonthString(2), "Feb")

    def test_shortMonthString_Mar(this):
        this.assertEqual(shortMonthString(3), "Mar")

    def test_shortMonthString_Apr(this):
        this.assertEqual(shortMonthString(4), "Apr")

    def test_shortMonthString_May(this):
        this.assertEqual(shortMonthString(5), "May")

    def test_shortMonthString_Jun(this):
        this.assertEqual(shortMonthString(6), "Jun")

    def test_shortMonthString_Jul(this):
        this.assertEqual(shortMonthString(7), "Jul")

    def test_shortMonthString_Aug(this):
        this.assertEqual(shortMonthString(8), "Aug")

    def test_shortMonthString_Sep(this):
        this.assertEqual(shortMonthString(9), "Sep")

    def test_shortMonthString_Oct(this):
        this.assertEqual(shortMonthString(10), "Oct")

    def test_shortMonthString_Nov(this):
        this.assertEqual(shortMonthString(11), "Nov")

    def test_shortMonthString_Dec(this):
        this.assertEqual(shortMonthString(12), "Dec")
