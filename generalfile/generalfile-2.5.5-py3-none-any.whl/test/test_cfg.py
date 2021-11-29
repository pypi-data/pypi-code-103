
from generalfile import Path
from generalfile.test.test_path import PathTest


class FileTest(PathTest):
    def test_cfg(self):
        dict_ = {'test': {'foo': 'bar', 'number': 2, 'hi': ['a', 'b', 3]}}

        Path("foo").cfg.write(dict_)
        self.assertEqual(dict_, Path("foo").cfg.read())

        dict_["test"]["foo"] = "hi"
        Path("foo").cfg.write(dict_, overwrite=True)
        self.assertEqual(dict_, Path("foo").cfg.read())

    def test_cfg_append(self):
        dict_ = {'setup': {'hello': 'random'}}
        Path("foo").cfg.write(dict_)

        dict_ = {'setup': {'foo': 'random'}, "test": {5: "bar"}}
        Path("foo").cfg.append(dict_)

        self.assertEqual({'setup': {'foo': 'random'}, 'test': {'5': 'bar'}}, Path("foo").cfg.read())

    def test_read_empty(self):
        with self.assertRaises(FileNotFoundError):
            Path("hey").cfg.read()
        self.assertEqual(None, Path("hi").cfg.read(default=None))
