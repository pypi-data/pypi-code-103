from pdx import utility_service

import unittest


class Testutility_service(unittest.TestCase):
    """
    Test utility methods
    """

    def test_ip_address(self):
        """
        Test determining IP address
        """
        ip = utility_service.get_ip_address()
        self.assertTrue(ip is not None, "You have no IP address?")
        self.assertTrue(type(ip) is str, "IP address should be a string")
        self.assertTrue(ip.count('.') == 3, "IP addresses have three dots")

    def test_max_len_in_list(self):
        """
        Test determining maximum string length in a list
        """
        self.assertTrue(utility_service.max_length_in_list(['a', 'b', 'c']) == 1, "Wrong max length. #1")
        self.assertTrue(utility_service.max_length_in_list(['abc', 'b', 'c']) == 3, "Wrong max length. #2")
        self.assertTrue(utility_service.max_length_in_list(['a', 'b', 'cba']) == 3, "Wrong max length. #3")
        self.assertTrue(utility_service.max_length_in_list([1234, 'b', 'c']) == 4, "Wrong max length. #5")
        self.assertTrue(utility_service.max_length_in_list([]) == 0, "Wrong max length. #6")
        self.assertTrue(utility_service.max_length_in_list(None) == 0, "Wrong max length. #7")


if __name__ == '__main__':
    unittest.main()
