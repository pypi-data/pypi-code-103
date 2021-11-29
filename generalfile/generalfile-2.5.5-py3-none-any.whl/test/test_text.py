
from generalfile import Path
from generalfile.test.test_path import PathTest


class TextTest(PathTest):
    paths = ("a", "b.txt", "c.md")

    def test_text_read_write(self):
        for path in self.paths:
            text = Path(path).text
            text.write("foo")
            self.assertEqual("foo", text.read())

            self.assertRaises(FileExistsError, text.write, "bar")

            text.write("bar", overwrite=True)
            self.assertEqual("bar", text.read())

    def test_text_append(self):
        for path in self.paths:
            text = Path(path).text

            text.append("foo")
            self.assertEqual("foo", text.read())

            text.append("bar")
            self.assertEqual("foobar", text.read())

            text.append("linebreak", newline=True)
            self.assertEqual("foobar\nlinebreak", text.read())

    def test_text_replace(self):
        for path in self.paths:
            text = Path(path).text

            text.write("hello this is a test")

            text.replace({"this": "that"})
            self.assertEqual("hello that is a test", text.read())

            text.replace({"that is": "what"})
            self.assertEqual("hello what a test", text.read())

            text.replace({"hello": "hi", "a test": "are tests"})
            self.assertEqual("hi what are tests", text.read())

    def test_text_replace_regex(self):
        for path in self.paths:
            text = Path(path).text

            text.write("hello this is a test")

            text.replace({".+": "foo52bar"}, regex=True)
            self.assertEqual("foo52bar", text.read())

            text.replace({".+": "foo52bar"}, regex=True)
            self.assertEqual("foo52bar", text.read())

            text.replace({"\d+": ""}, regex=True)
            self.assertEqual("foobar", text.read())

    def test_utf8(self):
        path = Path("foo")
        path.text.write("├")
        self.assertEqual("├", path.text.read())

    def test_read_empty(self):
        with self.assertRaises(FileNotFoundError):
            Path("hey").text.read()
        self.assertEqual(None, Path("hi").text.read(default=None))






























