#!/usr/bin/env python3
import collections
import unittest

import numpy.testing

from . import ringbuffer


class TestRingbuffer(unittest.TestCase):
    def setUp(self):
        pass

    def check_ringbuffer_deque(self, rb, deque, msg=None):
        if msg:
            err_msg = msg
        else:
            err_msg = ""

        self.assertEqual(len(rb), len(deque), msg=msg)

        if len(rb):
            numpy.testing.assert_equal(rb.get_last(), deque[-1],
                                       err_msg=err_msg)

            rb_elements = rb.get_contents()
            deque_elements = numpy.array(deque)
            numpy.testing.assert_equal(rb_elements, deque_elements,
                                       err_msg=err_msg)
        else:
            self.assertFalse(rb.get_contents(), msg=msg)
            self.assertFalse(numpy.array(deque), msg=msg)

    def test_append(self):
        for element_size in [1, 2]:
            rb = ringbuffer.RingBuffer(maxlen=5, element_size=element_size)
            deque = collections.deque(maxlen=5)

            self.check_ringbuffer_deque(rb, deque)

            for i in range(15):
                with self.subTest(element_size=element_size, i=i):
                    element = numpy.array([i] * element_size,
                                          dtype=numpy.float64)
                    rb.append(element)
                    deque.append(element)

                    self.check_ringbuffer_deque(rb, deque)

    def test_big_extends(self):
        maxlen = 10
        for element_size in [1, 2]:
            for array_size in [10, 15, 20, 25]:
                for initial in [0, 5]:
                    with self.subTest(element_size=element_size,
                                      array_size=array_size,
                                      initial=initial):
                        rb = ringbuffer.RingBuffer(maxlen=maxlen,
                                                   element_size=element_size)
                        deque = collections.deque(maxlen=maxlen)

                        if initial:
                            initial_array = numpy.random.rand(initial,
                                                              element_size)
                            rb.extend(initial_array)
                            deque.extend(initial_array)

                            self.check_ringbuffer_deque(rb, deque)

                        array = numpy.random.rand(array_size, element_size)
                        rb.extend(array)
                        deque.extend(array)

                        self.check_ringbuffer_deque(rb, deque)

    def test_small_extends(self):
        maxlen = 10
        for element_size in [1, 2]:
            for extend_size in range(1, 10):
                for initial in range(1, 10):
                    with self.subTest(element_size=element_size,
                                      extend_size=extend_size,
                                      initial=initial):
                        rb = ringbuffer.RingBuffer(maxlen=maxlen,
                                                   element_size=element_size)
                        deque = collections.deque(maxlen=maxlen)

                        if initial:
                            initial_array = numpy.random.rand(initial,
                                                              element_size)
                            rb.extend(initial_array)
                            deque.extend(initial_array)

                            self.check_ringbuffer_deque(rb, deque)

                        for i in range(100):
                            array = numpy.random.rand(extend_size,
                                                      element_size)
                            rb.extend(array)
                            deque.extend(array)

                            msg = "iteration={}".format(i + 1)
                            self.check_ringbuffer_deque(rb, deque, msg)

    def test_sequential_small_extends(self):
        maxlen = 10
        for element_size in [1, 2]:
            for extend_size in range(1, 10):
                for initial in range(1, 10):
                    with self.subTest(element_size=element_size,
                                      extend_size=extend_size,
                                      initial=initial):
                        rb = ringbuffer.RingBuffer(maxlen=maxlen,
                                                   element_size=element_size)
                        deque = collections.deque(maxlen=maxlen)

                        if initial:
                            initial_array = numpy.random.rand(initial,
                                                              element_size)
                            rb.extend(initial_array)
                            deque.extend(initial_array)

                            self.check_ringbuffer_deque(rb, deque)

                        for _i in range(100):
                            array = numpy.random.rand(extend_size,
                                                      element_size)
                            rb.extend(array)
                            deque.extend(array)

                        self.check_ringbuffer_deque(rb, deque)

    def test_clear(self):
        maxlen = 10
        for element_size in [1, 2]:
            for initial in [0, 7, 5, 10, 14, 15, 20]:
                with self.subTest(element_size=element_size,
                                  initial=initial):
                    rb = ringbuffer.RingBuffer(maxlen=maxlen,
                                               element_size=element_size)
                    deque = collections.deque(maxlen=maxlen)

                    initial_array = numpy.random.rand(initial,
                                                      element_size)
                    rb.extend(initial_array)
                    deque.extend(initial_array)

                    self.check_ringbuffer_deque(rb, deque)

                    rb.clear()
                    deque.clear()

                    self.check_ringbuffer_deque(rb, deque)

                    rb.extend(initial_array)
                    deque.extend(initial_array)

                    self.check_ringbuffer_deque(rb, deque)

    def test_zero_extend(self):
        maxlen = 10
        for element_size in [1, 2]:
            for initial in [0, 7, 5, 10, 14, 15, 20]:
                with self.subTest(element_size=element_size,
                                  initial=initial):
                    rb = ringbuffer.RingBuffer(maxlen=maxlen,
                                               element_size=element_size)
                    deque = collections.deque(maxlen=maxlen)

                    if initial:
                        initial_array = numpy.random.rand(initial,
                                                          element_size)
                        rb.extend(initial_array)
                        deque.extend(initial_array)

                    self.check_ringbuffer_deque(rb, deque)

                    element = numpy.empty((0, element_size))

                    rb.extend(element)
                    deque.extend(element)

                    self.check_ringbuffer_deque(rb, deque)


if __name__ == "__main__":
    unittest.main()
