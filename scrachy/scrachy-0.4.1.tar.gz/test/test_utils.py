#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

import unittest

from scrachy.utils.numeric import slice_int, to_int64, to_uint64


class TestUtils(unittest.TestCase):
    def test_slice_int(self):
        # Concatenate two 64bit integers into one 128bit integer and make sure
        # we get back the first integer when slicing the first 64 bits.
        first_int, second_int = 167, 572
        large_int = first_int.to_bytes(8, 'big') + second_int.to_bytes(8, 'big')

        act_int = slice_int(large_int, 64)
        self.assertEqual(first_int, act_int)

        # Make sure we get back the same value we put in if it can be
        # represented by the given number of bits.
        act_int = slice_int(first_int.to_bytes(4, 'big'), 32)
        exp_int = first_int

        self.assertEqual(act_int, exp_int)

        # Most of the bytes at the front of this integer are 0, so slicing
        # only the first 32 bits will return 0.
        act_int = slice_int(first_int.to_bytes(8, 'big'), 32)
        exp_int = 0

        self.assertEqual(act_int, exp_int)

    def test_signed_to_unsigned(self):
        max_unsigned = 18446744073709551615

        act_signed = to_int64(max_unsigned)
        exp_signed = -1

        self.assertEqual(act_signed, exp_signed)

        act_unsigned = to_uint64(exp_signed)
        exp_unsigned = max_unsigned

        self.assertEqual(act_unsigned, exp_unsigned)


if __name__ == '__main__':
    unittest.main()
