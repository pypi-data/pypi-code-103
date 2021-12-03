
from generalfile import Path
from generalfile.test.test_path import PathTest


class A:
    def __init__(self, x):
        self.x = x

class FileTest(PathTest):
    def test_pickle(self):
        Path("hi.txt").pickle.write(A(53))
        a = Path("hi.txt").pickle.read()
        self.assertEqual(53, a.x)

    def test_pickle_list(self):
        Path("hi.txt").pickle.write([A("hi"), A(53)])
        l = Path("hi.txt").pickle.read()
        self.assertEqual("hi", l[0].x)
        self.assertEqual(53, l[1].x)

    def test_read_empty(self):
        with self.assertRaises(FileNotFoundError):
            Path("hey").pickle.read()
        self.assertEqual(None, Path("hi").pickle.read(default=None))
