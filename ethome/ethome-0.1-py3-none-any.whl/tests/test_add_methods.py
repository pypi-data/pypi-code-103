import unittest
import numpy as np
from ethome import Ethome
from suit import Suit
from glasses import Glasses
from device import Device


class TestAddMethods(unittest.TestCase):
    e = Ethome()
    e.add_devices(s=Suit())
    def test_ethome_adds_suit(self):
        self.assertTrue(self.e.s)

    def test_time_vectors_are_numpy_arrays(self):
        pass

    def test_ethome_can_generate_time_vector(self):
        testarray1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        testarray2 = np.array([1, 2, 3, 4, 5])
        self.e.generate_time_vector(testarray1, testarray2)
        #needs the assert statement here
    
    def test_list_keys_returns_keys(self):
        self.assertTrue(self.e.list_keys(self.e))