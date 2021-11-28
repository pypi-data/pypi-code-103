# pylint: skip-file
import unittest

from .. import Repository


class ClassCreationTestCase(unittest.TestCase):

    def test_create_class(self):

        class Impl:
            pass

        repo = Repository.new(Impl)

    def test_with_context(self):

        class Impl:

            def setup_context(self, foo):
                self.foo = foo

        repo = Repository.new(Impl)
        with repo.with_context(foo=1) as tmp:
            self.assertEqual(tmp.foo, 1)

    def test_with_context_can_not_be_nested(self):

        class Impl:

            def setup_context(self, foo):
                self.foo = foo

        repo = Repository.new(Impl)
        with repo.with_context(foo=1) as tmp:
            with self.assertRaises(RuntimeError):
                with tmp.with_context(foo=1) as tmp:
                    self.fail()
