
import unittest
from generalvector.vector import Vec

class VecTest(unittest.TestCase):
    def test_vec(self):
        self.assertRaises(ValueError, Vec, "")
        self.assertRaises(ValueError, Vec, 5, 2, "")
        self.assertRaises(ValueError, Vec, 5, "", 2)

        self.assertRaises(AttributeError, Vec, 2, 5)


        self.assertEqual(Vec(5.2, 2, 3), Vec("5.2", "2", 3))

        self.assertEqual(Vec(None).x, Vec(0))
        self.assertEqual(Vec(None, 5).x, 5)
        self.assertEqual(Vec(5, None).x, 5)
        self.assertEqual(Vec(5, 2, 1).x, 5)
        self.assertEqual(Vec(5, 2, 1).y, 2)
        self.assertEqual(Vec(5, 2, 1).z, 1)

        self.assertEqual(Vec(5.2, 2.5, 1.4).x, 5.2)
        self.assertEqual(Vec(5.2, 2.5, 1.4).y, 2.5)
        self.assertEqual(Vec(5.2, 2.5, 1.4).z, 1.4)

        self.assertEqual(Vec(5).x, 5)
        self.assertEqual(Vec(5).y, 5)
        self.assertEqual(Vec(5).z, 5)

        self.assertEqual(Vec(5, 2, 1), Vec(Vec(5, 2, 1)))

    def test_equal(self):
        self.assertRaises(TypeError, Vec.__eq__, "")

        self.assertTrue(Vec(1) == Vec(1))
        self.assertTrue(Vec(1, 2, 3) == Vec(1, 2, 3))
        self.assertTrue(Vec(1, 1, 1) == 1)
        self.assertTrue(Vec(5.2, 5.2, 5.2) == 5.2)

        self.assertFalse(Vec(1, 2, 3) == Vec(1, 3, 3))
        self.assertFalse(Vec(1, 2, 3) == Vec(2, 2, 3))

        self.assertFalse(Vec(1, 1, 3) == 2)
        self.assertFalse(Vec(5.2, 5.2, 3) == 5)

        self.assertFalse(Vec(5.2, 5.2, 5.2) is None)
        self.assertFalse(Vec(5.2, 5.2, 5.2) == "test")

    def test_add(self):
        self.assertRaises(TypeError, Vec.__add__, "")
        self.assertRaises(TypeError, Vec.__add__, False)

        self.assertEqual(Vec(5, 2, 3) + Vec(2, 4, 3), Vec(7, 6, 6))
        self.assertEqual(Vec(5, 2, 3) + Vec(2.5, 4.5, 3.5), Vec(7.5, 6.5, 6.5))
        self.assertEqual(Vec(5, 2, 3) + Vec(-2, -4, -3), Vec(3, -2, 0))

        self.assertEqual(Vec(5, 2, 3) + 3, Vec(8, 5, 6))
        self.assertEqual(Vec(5, 2, 3) + -3, Vec(2, -1, 0))
        self.assertEqual(Vec(5, 2, 3) + 3.5, Vec(8.5, 5.5, 6.5))

    def test_sub(self):
        self.assertRaises(TypeError, Vec.__sub__, "")
        self.assertRaises(TypeError, Vec.__sub__, True)

        self.assertEqual(Vec(5, 2, 3) - Vec(2, 4, 3), Vec(3, -2, 0))
        self.assertEqual(Vec(5, 2, 3) - Vec(-2, -4, -3), Vec(7, 6, 6))
        self.assertEqual(Vec(5, 2, 3) - 3, Vec(2, -1, 0))
        self.assertEqual(Vec(5, 2, 3) - -3, Vec(8, 5, 6))
        self.assertEqual(Vec(5, 2, 3) - 3.5, Vec(1.5, -1.5, -0.5))

    def test_mul(self):
        self.assertRaises(TypeError, Vec.__mul__, "")
        self.assertRaises(TypeError, Vec.__mul__, True)

        self.assertEqual(Vec(5, 2, 3) * 2, Vec(10, 4, 6))
        self.assertEqual(Vec(5, 2, 3) * 2.5, Vec(12.5, 5, 7.5))

        self.assertEqual(Vec(5, 2, 3) * Vec(2, 1, 3), Vec(10, 2, 9))

    def test_div(self):
        self.assertRaises(TypeError, Vec.__truediv__, "")
        self.assertRaises(TypeError, Vec.__truediv__, False)

        self.assertEqual(Vec(5, 2, 3) / 2, Vec(2.5, 1, 1.5))
        self.assertEqual(Vec(10, 5, 7.5) / 2.5, Vec(4, 2, 3))

        self.assertEqual(Vec(10, 5, 7.5) / Vec(5, 2, 2.5), Vec(2, 2.5, 3))

    def test_length(self):
        self.assertEqual(Vec(10, 0, 0).length(), 10)
        self.assertEqual(Vec(0, 10, 0).length(), 10)
        self.assertEqual(Vec(0, 0, 10).length(), 10)
        self.assertEqual(Vec(0, 0.2, 0).length(), 0.2)
        self.assertEqual(Vec(0, 0, 0).length(), 0)

    def test_normalized(self):
        self.assertEqual(Vec(10, 0, 0).normalized(), Vec(1, 0, 0))
        self.assertEqual(Vec(0, 10, 0).normalized(), Vec(0, 1, 0))
        self.assertEqual(Vec(0, 0.2, 0).normalized(), Vec(0, 1, 0))
        self.assertEqual(Vec(0, 0, 0).normalized(), Vec(0, 0, 0))
        self.assertEqual(Vec(0, -10, 0).normalized(), Vec(0, -1, 0))

    def test_round(self):
        self.assertEqual(Vec(5, 2, 1), Vec(5.3, 1.5, 1.4).round())

    def test_random(self):
        randvec = Vec.random(5)
        self.assertGreaterEqual(randvec.x, 0)
        self.assertGreaterEqual(randvec.y, 0)
        self.assertGreaterEqual(randvec.z, 0)
        self.assertLessEqual(randvec.x, 5)
        self.assertLessEqual(randvec.y, 5)
        self.assertLessEqual(randvec.z, 5)

        randvec = Vec.random(3, 5)
        self.assertGreaterEqual(randvec.x, 3)
        self.assertGreaterEqual(randvec.y, 3)
        self.assertGreaterEqual(randvec.z, 3)
        self.assertLessEqual(randvec.x, 5)
        self.assertLessEqual(randvec.y, 5)
        self.assertLessEqual(randvec.z, 5)

        randvec = Vec.random(Vec(-1, 2, 6))
        self.assertGreaterEqual(randvec.x, -1)
        self.assertGreaterEqual(randvec.y, 0)
        self.assertGreaterEqual(randvec.z, 0)
        self.assertLessEqual(randvec.x, 0)
        self.assertLessEqual(randvec.y, 2)
        self.assertLessEqual(randvec.z, 6)

        randvec = Vec.random(Vec(4, 2, 6), 8)
        self.assertGreaterEqual(randvec.x, 4)
        self.assertGreaterEqual(randvec.y, 2)
        self.assertGreaterEqual(randvec.z, 6)
        self.assertLessEqual(randvec.x, 8)
        self.assertLessEqual(randvec.y, 8)
        self.assertLessEqual(randvec.z, 8)

        randvec = Vec.random(8, Vec(4, 2, 6))
        self.assertGreaterEqual(randvec.x, 4)
        self.assertGreaterEqual(randvec.y, 2)
        self.assertGreaterEqual(randvec.z, 6)
        self.assertLessEqual(randvec.x, 8)
        self.assertLessEqual(randvec.y, 8)
        self.assertLessEqual(randvec.z, 8)

        randvec = Vec.random(Vec(3.5, 3, 10), Vec(4, 2, 6))
        self.assertGreaterEqual(randvec.x, 3.5)
        self.assertGreaterEqual(randvec.y, 2)
        self.assertGreaterEqual(randvec.z, 6)
        self.assertLessEqual(randvec.x, 4)
        self.assertLessEqual(randvec.y, 3)
        self.assertLessEqual(randvec.z, 10)

    def test_min(self):
        self.assertEqual(Vec(5, 2, 1), Vec(8, 2, 10).min(Vec(5, 5, 1)))
        self.assertEqual(Vec(5, 2, 1), Vec(10).min(Vec(5, 2, 1)))
        self.assertEqual(Vec(5, 2, -1), Vec(5, 2, -1).min(Vec(99)))
        self.assertEqual(Vec(5, 5, 5), Vec(6.5).min(Vec(5)))
        self.assertEqual(Vec(5.5, 5.5, 5.5), Vec(6.5).min(Vec(5.5)))

    def test_max(self):
        self.assertEqual(Vec(8, 5, 10), Vec(8, 2, 10).max(Vec(5, 5, 1)))
        self.assertEqual(Vec(10), Vec(10).max(Vec(5, 2, 1)))
        self.assertEqual(Vec(99), Vec(5, 2, -1).max(Vec(99)))
        self.assertEqual(Vec(6.5), Vec(6.5).max(Vec(5)))
        self.assertEqual(Vec(6.5), Vec(6.5).max(Vec(5.5)))

    def test_clamp(self):
        self.assertEqual(Vec(5, 2, 1), Vec(6, 2, 1).clamp(0, 5))
        self.assertEqual(Vec(5, 2, 1), Vec(0).clamp(Vec(5, 2, 1), 5))
        self.assertEqual(Vec(-3, 2, 1), Vec(0).clamp(Vec(-3, 2, 1), Vec(-3, 2, 1)))
        self.assertEqual(Vec(-3, 2, 1), Vec(0).clamp(Vec(-30, 2, 1), Vec(-3, 20, 10)))

    def test_inrange(self):
        self.assertEqual(True, Vec(5).inrange(Vec(4), Vec(6)))
        self.assertEqual(True, Vec(5).inrange(Vec(5), Vec(5)))
        self.assertEqual(True, Vec(2, 3, 4).inrange(Vec(1, 2, 3), Vec(5)))

        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(1, 2, 3), Vec(5, 5, 3)))
        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(1, 2, 3), Vec(5, 2, 5)))
        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(1, 2, 3), Vec(1, 5, 5)))

        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(3, 2, 3), Vec(5)))
        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(1, 4, 3), Vec(5)))
        self.assertEqual(False, Vec(2, 3, 4).inrange(Vec(1, 2, 5), Vec(5)))

    def test_hex(self):
        self.assertEqual("#c8c800", Vec(200, 200, 0).hex())
        self.assertEqual("#ff0000", Vec(255, 0, 0).hex())
        self.assertEqual("#ff0000", Vec(300, -2, -100).hex())
        self.assertEqual("#ff1632", Vec(255, 22, 50).hex())

    def test_lessThan(self):
        self.assertEqual(True, Vec(10) < Vec(11))
        self.assertEqual(False, Vec(10) < Vec(10))
        self.assertEqual(True, Vec(10, 10, 10) < Vec(11, 15, 14))
        self.assertEqual(False, Vec(10, 10, 10) < Vec(9, 15, 14))
        self.assertEqual(False, Vec(10, 10, 10) < Vec(10, 15, 14))
        self.assertEqual(False, Vec(10, 10, 10) < Vec(9, 9, 9))

    def test_greaterThan(self):
        self.assertEqual(False, Vec(10) > Vec(11))
        self.assertEqual(False, Vec(10) > Vec(10))
        self.assertEqual(False, Vec(10, 10, 10) > Vec(11, 15, 14))
        self.assertEqual(False, Vec(10, 10, 10) > Vec(9, 15, 14))
        self.assertEqual(False, Vec(10, 10, 10) > Vec(10, 5, 4))
        self.assertEqual(True, Vec(10, 10, 10) > Vec(9, 9, 9))

    def test_lessThanOrEqual(self):
        self.assertEqual(True, Vec(5) <= Vec(5))
        self.assertEqual(True, Vec(4) <= Vec(5))
        self.assertEqual(False, Vec(6) <= Vec(5))
        self.assertEqual(True, Vec(10, 10, 10) <= Vec(10, 15, 14))

    def test_greaterThanOrEqual(self):
        self.assertEqual(True, Vec(5) >= Vec(5))
        self.assertEqual(True, Vec(6) >= Vec(5))
        self.assertEqual(False, Vec(4) >= Vec(5))
        self.assertEqual(True, Vec(10, 10, 10) >= Vec(10, 9, 7))

    def test_range(self):
        self.assertRaises(ValueError, Vec(0, -1, 0).range, Vec(-1, -1, 1))
        self.assertRaises(ValueError, Vec(0, -1, 0).range, Vec(-1, 1, 1))
        self.assertRaises(ValueError, Vec(0, -1.2, 0).range, Vec(1, 1, 1))
        self.assertRaises(ValueError, Vec(0, 0, 0).range, Vec(1, 1.1, 1))

        self.assertEqual([Vec(0, 0, 0)], Vec(0, 0, 0).range(Vec(1, 1, 1)))
        self.assertEqual([Vec(0, 0, 0), Vec(1, 0, 0)], Vec(0, 0, 0).range(Vec(2, 1, 1)))
        self.assertEqual([Vec(0, 0, 0), Vec(0, 1, 0), Vec(0, 0, 1), Vec(0, 1, 1)], Vec(0, 0, 0).range(Vec(1, 2, 2)))
        self.assertEqual([Vec(0, 1, 0), Vec(0, 2, 0), Vec(0, 3, 0)], Vec(0, 1, 0).range(Vec(1, 3, 1)))
        self.assertEqual([Vec(2, 2, 2), Vec(3, 2, 2), Vec(2, 3, 2), Vec(3, 3, 2), Vec(2, 2, 3), Vec(3, 2, 3), Vec(2, 3, 3), Vec(3, 3, 3)], Vec(2).range(Vec(2)))

        self.assertEqual([], Vec(2).range(Vec(0, 1, 2)))
        self.assertEqual([], Vec(2).range(Vec(1, 0, 2)))
        self.assertEqual([], Vec(2).range(Vec(1, 3, 0)))
        self.assertEqual([], Vec(2).range(Vec(0, 0, 0)))

    def test_distance(self):
        self.assertEqual(5, Vec(10, 5, 0).distance(Vec(15, 5, 0)))
        self.assertEqual(5, Vec(10, 5, 0).distance(Vec(5, 5, 0)))
        self.assertEqual(0, Vec(10, 5, 0).distance(Vec(10, 5, 0)))
        self.assertEqual(2, Vec(-2, 0, 0).distance(Vec(0, 0, 0)))
        self.assertEqual(2, Vec(0, 0, 0).distance(Vec(-2, 0, 0)))
        self.assertEqual(2, Vec(0, 0, 2).distance(Vec(0, 0, 0)))

    def test_sanitize(self):
        self.assertRaises(ValueError, Vec(0.5).sanitize, ints=True)
        self.assertRaises(ValueError, Vec(0).sanitize, positive=True)
        self.assertRaises(ValueError, Vec(-1).sanitize, positive=True)
        self.assertRaises(ValueError, Vec(-1).sanitize, positiveOrZero=True)
        self.assertRaises(ValueError, Vec(0).sanitize, negative=True)
        self.assertRaises(ValueError, Vec(1).sanitize, negative=True)
        self.assertRaises(ValueError, Vec(1).sanitize, negativeOrZero=True)
        self.assertRaises(ValueError, Vec(1).sanitize, minimum=Vec(2))
        self.assertRaises(ValueError, Vec(1).sanitize, maximum=Vec(0))

        self.assertTrue(Vec(1).sanitize(ints=True))
        self.assertTrue(Vec(1).sanitize(positive=True))
        self.assertTrue(Vec(0).sanitize(positiveOrZero=True))
        self.assertTrue(Vec(1).sanitize(positiveOrZero=True))
        self.assertTrue(Vec(-1).sanitize(negative=True))
        self.assertTrue(Vec(0).sanitize(negativeOrZero=True))
        self.assertTrue(Vec(-1).sanitize(negativeOrZero=True))
        self.assertTrue(Vec(1).sanitize(minimum=Vec(1)))
        self.assertTrue(Vec(1).sanitize(maximum=Vec(1)))

    def test_confineTo(self):
        self.assertEqual(Vec(1, 1, 1), Vec(11, 11, 11).confineTo(Vec(0, 0, 0), Vec(10, 10, 10)))
        self.assertEqual(Vec(1, 1, 1), Vec(11, 11, 11).confineTo(Vec(-1, 0, 0), Vec(10, 10, 10)))
        self.assertEqual(Vec(2, 7, 5), Vec(22, -13, 5).confineTo(Vec(0, 0, 0), Vec(10, 10, 10)))

        self.assertEqual(Vec(0), Vec(2).confineTo(Vec(0), Vec(1), margin=0.5))

    def test_absolute(self):
        self.assertEqual(Vec(1, 2, 3), Vec(1, 2, 3).absolute())
        self.assertEqual(Vec(1, 2, 3), Vec(-1, 2, 3).absolute())
        self.assertEqual(Vec(1, 2, 3), Vec(1, -2, 3).absolute())
        self.assertEqual(Vec(1, 2, 3), Vec(1, 2, -3).absolute())
        self.assertEqual(Vec(1, 2, 3), Vec(-1, -2, -3).absolute())
        self.assertEqual(Vec(1.1, 2, 3), Vec(-1.1, -2, -3).absolute())
















