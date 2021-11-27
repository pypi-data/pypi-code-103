
import unittest
import multiprocessing as mp

from generalfile import *
from generalfile.test.setup_workdir import setup_workdir


def _thread_test(queue, i):
    queue.put(int(Path("test.txt").write(i, overwrite=True)))


class PathTest(unittest.TestCase):
    def setUp(self):
        """Set working dir and clear folder. Set path delimiter to '/' for testing."""
        setup_workdir()


class FileTest(PathTest):
    """ Skipped: open_folder, view, scrub"""
    def test_path(self):
        self.assertRaises(InvalidCharacterError, Path, "hello:there")
        self.assertRaises(InvalidCharacterError, Path, "hello<")
        self.assertRaises(InvalidCharacterError, Path, "hello>")
        self.assertRaises(InvalidCharacterError, Path, "hello.")

    def test_addPath(self):
        self.assertEqual(Path("foo/bar"), Path("foo") / "bar")
        self.assertEqual(Path("foo/bar"), Path("foo") / Path("bar"))
        self.assertEqual(Path("foo.txt/folder"), Path("foo.txt") / "folder")
        self.assertEqual(Path("folder/foo.txt"), Path("folder") / "foo.txt")

    def test_parts(self):
        path = Path("folder/folder2/test.txt")
        self.assertEqual(["folder", "folder2", "test.txt"], path.parts())

        self.assertEqual("foo", Path("foo/bar").parts()[0])
        self.assertEqual("bar", Path("foo/bar").parts()[1])

        self.assertEqual(not Path.verInfo.pathRootIsDelimiter, bool(Path().absolute().parts()[0]))

    def test_name(self):
        path = Path("folder/test.txt")
        self.assertEqual("test.txt", path.name())

        self.assertEqual("folder/foobar.txt", path.with_name("foobar.txt"))
        self.assertEqual("folder/hi", path.with_name("hi"))

    def test_stem(self):
        path = Path("folder/test.txt")
        self.assertEqual("test", path.stem())
        self.assertEqual("folder/foobar.txt", path.with_stem("foobar"))

        path = Path("folder/test.foo.txt.bar")
        self.assertEqual("test.foo.txt", path.stem())
        self.assertEqual("folder/foo.bar", path.with_stem("foo"))

    def test_true_stem(self):
        path = Path("folder/test.txt")
        self.assertEqual("test", path.true_stem())
        self.assertEqual("folder/foobar.txt", path.with_true_stem("foobar"))

        path = Path("folder/test.foo.txt.bar")
        self.assertEqual("test", path.true_stem())
        self.assertEqual("folder/yo.foo.txt.bar", path.with_true_stem("yo"))

    def test_suffixes(self):
        path = Path("folder/test.hello.txt")
        self.assertEqual([".hello", ".txt"], path.suffixes())
        self.assertEqual("folder/test.tsv", path.with_suffixes(".tsv"))

    def test_suffix(self):
        path = Path("folder/test")
        self.assertEqual("", path.suffix())

        path = Path("folder/test.txt")
        self.assertEqual(".txt", path.suffix())

        path = path.with_suffix("")
        self.assertEqual("folder/test", path)

        path = path.with_suffix(None)
        self.assertEqual("folder/test", path)

        path = path.with_suffix(".tsv")
        self.assertEqual("folder/test.tsv", path)

        path = path.with_suffix("")
        self.assertEqual("folder/test", path)

        path = path.with_suffix(".csv")
        self.assertEqual("folder/test.csv", path)

        path = path.with_suffix(".BACKUP", -2)
        self.assertEqual("folder/test.BACKUP.csv", path)

        path = path.with_suffix(".test", -2)
        self.assertEqual("folder/test.test.csv", path)

        path = path.with_suffix(None, 0)
        self.assertEqual("folder/test.csv", path)

        path = path.with_suffix(".foo", 2)
        self.assertEqual("folder/test.csv.foo", path)

        path = path.with_suffix(".bar", 3)
        self.assertEqual("folder/test.csv.foo.bar", path)

        path = path.with_suffix(".clamped", 5)
        self.assertEqual("folder/test.csv.foo.bar.clamped", path)

        path = path.with_suffix(".clamped", -10)
        self.assertEqual("folder/test.clamped.csv.foo.bar.clamped", path)

        path = path.with_suffix(None, 10)
        self.assertEqual("folder/test.clamped.csv.foo.bar", path)

        path = path.with_suffix(None, -10)
        self.assertEqual("folder/test.csv.foo.bar", path)

    def test_parent(self):
        path = Path("folder/foobar/test.txt")
        self.assertEqual(Path("folder/foobar"), path.get_parent())
        self.assertEqual(Path("folder/foobar"), path.get_parent(0))
        self.assertEqual(Path("folder"), path.get_parent(1, 1))
        self.assertEqual(Path(), path.get_parent(2, 2))
        self.assertEqual(None, path.get_parent(3, 3))
        self.assertEqual(None, path.get_parent(99, 99))
        self.assertEqual(None, path.get_parent(-99, -99))

        self.assertEqual([Path("folder/foobar"), Path("folder"), Path()], path.get_parents(depth=-1))
        new_path = Path("folder/foobar/test.txt")
        self.assertEqual([Path("folder/foobar"), Path("folder"), Path()], new_path.get_parents(depth=-1))

    def test_startswith(self):
        self.assertFalse(Path("file.txt").startswith("folder"))
        self.assertTrue(Path("file.txt").startswith("file"))
        self.assertFalse(Path("folder/file.txt").startswith("file.txt"))
        self.assertFalse(Path("folder/file.txt").absolute().startswith("folder"))

        self.assertTrue(Path("folder/file.txt").startswith("folder"))
        self.assertTrue(Path("file.txt").startswith("file.txt"))
        self.assertTrue(Path("file.SUFFIX.txt").startswith("file.SUFFIX.txt"))
        self.assertFalse(Path("filE.txt").startswith("file.txt"))

    def test_endswith(self):
        self.assertFalse(Path("file.txt").endswith("folder"))
        self.assertFalse(Path("file.txt").endswith("file"))
        self.assertFalse(Path("folder/file.txt").endswith("folder"))
        self.assertFalse(Path("folder/file.txt").absolute().endswith("file"))

        self.assertTrue(Path("folder/file.txt").endswith("file.txt"))
        self.assertTrue(Path("folder/file.txt").endswith("txt"))
        self.assertTrue(Path("file.txt").endswith("file.txt"))
        self.assertFalse(Path("filE.txt").endswith("file.txt"))

    def test_remove_start(self):
        self.assertEqual(Path(), Path("test.txt").remove_start("test.txt"))
        self.assertEqual(Path("folder/test.txt"), Path("folder/test.txt").remove_start("Folder"))
        self.assertEqual(Path("test.txt"), Path("folder/test.txt").remove_start("folder"))
        self.assertEqual(Path("folder/test.txt"), Path("folder/test.txt").remove_start("test"))

        if Path.verInfo.pathRootIsDelimiter:
            self.assertEqual(Path("test.txt"), Path("folder/test.txt").remove_start("folder"))


    def test_remove_end(self):
        self.assertEqual(Path(), Path("test.txt").remove_end("test.txt"))
        self.assertEqual(Path("test"), Path("test.txt").remove_end(".txt"), "test")
        self.assertEqual(Path("folder"), Path("folder/test.txt").remove_end("test.txt"))
        self.assertEqual(Path("folder/test.txt"), Path("folder/test.txt").remove_end("test"))

    def test_absolute(self):
        path = Path("test.txt")
        self.assertEqual(False, path.is_absolute())
        self.assertEqual(True, path.is_relative())

        path = path.absolute()
        self.assertEqual(True, path.is_absolute())
        self.assertEqual(False, path.is_relative())

        path = path.relative()
        self.assertEqual(False, path.is_absolute())
        self.assertEqual(True, path.is_relative())

        path = Path("folder/folder2/file.txt")
        self.assertEqual(Path("folder2/file.txt"), path.relative("folder"))
        self.assertEqual(path.relative("folder"), "folder2/file.txt")
        self.assertEqual(path.relative("folder/folder2"), "file.txt")

        self.assertEqual(path, path.relative("doesntexist"))

    def test_mirror_path(self):
        path = Path("foo")
        self.assertEqual(path.mirror_path().mirror_path(), path)
        self.assertEqual(True, path.mirror_path().is_absolute())

    def test_is_file_or_folder(self):
        Path("folder.txt/file.txt").write()
        self.assertEqual(True, Path("folder.txt").is_folder())
        self.assertEqual(False, Path("folder.txt").is_file())

        self.assertEqual(True, Path("folder.txt/file.txt").is_file())
        self.assertEqual(False, Path("folder.txt/file.txt").is_folder())

    def test_exists(self):
        path = Path("folder/test.txt")
        self.assertEqual(False, path.exists())
        self.assertEqual(False, Path("folder").exists())

        path.write()
        self.assertEqual(True, path.exists())
        self.assertEqual(True, Path("folder").exists())
        self.assertEqual(False, Path("folder/test").exists())

        Path("folder").delete()
        self.assertEqual(False, path.exists())
        self.assertEqual(False, Path("folder").exists())

    def test_working_dir(self):
        self.assertEqual(True, Path.get_working_dir().is_absolute())
        self.assertEqual(Path().absolute(), Path.get_working_dir())

        Path("folder").set_working_dir()
        self.assertEqual(True, Path.get_working_dir().endswith("folder"))
        self.assertEqual(Path().absolute(), Path.get_working_dir())

    def test_same_destination(self):
        path = Path("folder")
        self.assertEqual(True, path.same_destination(Path() / "folder"))
        self.assertEqual(True, path.same_destination(path.absolute()))
        self.assertEqual(True, path.same_destination("folder"))

    def test_write(self):
        self.assertEqual('"foobar"', Path("test.txt").write("foobar"))
        self.assertEqual("foobar", Path("test.txt").read())

        self.assertEqual('"foobar"', Path("test2").write("foobar"))
        self.assertEqual("foobar", Path("test2").read())

        self.assertEqual('"foobar"', Path("test2.doesntexist").write("foobar"))
        self.assertEqual("foobar", Path("test2.doesntexist").read())

        self.assertEqual('"foobar"', Path("folder/test.txt").write("foobar"))
        self.assertEqual("foobar", Path("folder/test.txt").read())

    def test_rename(self):
        Path("folder/test.txt").write()

        Path("folder/test.txt").rename(name="hello.txt")
        self.assertTrue(Path("folder/hello.txt").exists())
        self.assertFalse(Path("folder/test.txt").exists())

        Path("folder").rename(name="folder2")
        self.assertTrue(Path("folder2").exists())
        self.assertFalse(Path("folder").exists())

        Path("folder2/hello.txt").rename(name="foo.txt")
        self.assertTrue(Path("folder2/foo.txt").exists())

        Path("folder2/foo.txt").rename(name="foo.TEST.txt")
        self.assertTrue(Path("folder2/foo.TEST.txt").exists())

        Path("folder2/foo.TEST.txt").rename(name="foobar")
        self.assertTrue(Path("folder2/foobar").is_file())

        Path("folder2/foobar").rename(suffix=".test")
        self.assertTrue(Path("folder2/foobar.test").exists())

        self.assertEqual("folder2/hello.test", Path("folder2/foobar.test").rename(stem="hello"))
        self.assertTrue(Path("folder2/hello.test").exists())

    def test_copy(self):
        Path("folder/test.txt").write()
        Path("folder/test.txt").copy("foo.txt")
        self.assertEqual(True, Path("folder/foo.txt").exists())

        Path("folder").copy("new")
        self.assertEqual(True, Path("new/foo.txt").exists())

        Path("new/foo.txt").copy("new/bar.txt")
        self.assertEqual(True, Path("new/bar.txt").exists())

    def test_copy_to_folder(self):
        Path("folder/test.txt").write()
        Path("folder/test2.txt").write()

        Path("folder").copy_to_folder("folder2")
        self.assertEqual(True, Path("folder2/test.txt").exists())
        self.assertEqual(True, Path("folder2/test2.txt").exists())
        self.assertEqual(True, Path("folder/test2.txt").exists())

        Path("folder/test.txt").copy_to_folder("")
        self.assertEqual(True, Path("test.txt").exists())
        self.assertEqual(False, Path("test2.txt").exists())

        Path("folder").copy_to_folder(Path(), overwrite=True)
        self.assertEqual(True, Path("test2.txt").exists())

    def test_move(self):
        Path("folder/test.txt").write(5)
        Path("folder/test2.txt").write()

        Path("folder").move("folder2")
        self.assertEqual(False, Path("folder").exists())
        self.assertEqual(True, Path("folder2/test.txt").exists())
        self.assertEqual(True, Path("folder2/test2.txt").exists())

        Path("folder2/test.txt").move("")
        self.assertEqual(True, Path("test.txt").exists())
        self.assertEqual(False, Path("test2.txt").exists())
        self.assertEqual(False, Path("folder2/test.txt").exists())

        Path("folder/test.txt").write(2)
        with self.assertRaises(FileExistsError):
            Path("folder").move(Path())

        self.assertEqual(5, Path("test.txt").read())
        Path("folder").move(Path(), overwrite=True)
        self.assertEqual(2, Path("test.txt").read())

    def test_create_folder(self):
        path = Path("folder/folder2.txt")
        path.create_folder()

        self.assertEqual(True, path.is_folder())

    def test_trash_and_delete(self):
        for method in ("trash", "delete"):
            path = Path("file.txt")
            self.assertEqual(False, path.exists())
            self.assertEqual(False, getattr(path, method)())

            path.write()
            self.assertEqual(True, path.exists())
            self.assertEqual(True, getattr(path, method)())
            self.assertEqual(False, getattr(path, method)())

            path = Path("folder/file.txt")
            self.assertEqual(False, path.exists())
            self.assertEqual(False, getattr(path, method)())

            path.write()
            self.assertEqual(True, path.exists())
            self.assertEqual(True, getattr(path.get_parent(), method)())
            self.assertEqual(False, getattr(path.get_parent(), method)())
            self.assertEqual(False, Path("folder").exists())

    def test_trash_and_delete_folder_content(self):
        for method in ("trash_folder_content", "delete_folder_content"):
            setup_workdir()

            mainPath = Path("folder")
            path = mainPath / "file.txt"
            path2 = mainPath / "folder2/file2.txt"
            self.assertEqual(False, mainPath.exists())
            self.assertEqual(False, getattr(mainPath, method)())

            for targetPath in (mainPath, ):
                path.write()
                path2.write()
                self.assertEqual(True, getattr(targetPath, method)())
                self.assertEqual(False, getattr(targetPath, method)())
                self.assertEqual(True, mainPath.exists())
                self.assertEqual(False, path.exists())
                self.assertEqual(False, path2.exists())

    def test_get_paths(self):
        Path("test.txt").write()
        Path("folder/test2.txt").write()
        Path("folder/test3.txt").write()

        self.assertEqual(2, len(Path().get_children()))
        self.assertEqual(3, len(Path().get_children(include_self=True)))

        self.assertEqual(0, len(Path("test.txt").get_children()))
        self.assertEqual(1, len(Path("test.txt").get_children(include_self=True)))
        self.assertEqual(0, len(Path("test.txt").get_children()))

        self.assertEqual(4, len(Path().get_children(depth=3)))
        self.assertEqual(5, len(Path().get_children(depth=1, include_self=True)))
        self.assertEqual(5, len(Path().get_children(depth=-1, include_self=True)))
        self.assertEqual(3, len(Path().get_children(depth=0, include_self=True)))

        self.assertEqual(0, len(Path("folder/test2.txt").get_children(depth=-1)))

        self.assertEqual(["folder/test2.txt", "folder/test3.txt"], Path("folder").get_children())

    def test_time_created_and_modified(self):
        path = Path("test.txt")
        methods = (path.seconds_since_creation, path.seconds_since_modified)

        for method in methods:
            self.assertRaises(AttributeError, method)

        path.write()

        for method in methods:
            self.assertGreater(method(), 0)

        # Think you need to flush and stuff to make this work for windows atleast
        # self.assertEqual(methods[0](), methods[1]())
        # path.write("foobar", overwrite=True)
        # self.assertNotEqual(methods[0](), methods[1]())

    def test_getitem(self):
        self.assertEqual("f", Path("foobar")[0])
        self.assertEqual("fo", Path("foobar")[0:2])
        self.assertEqual("raboof", Path("foobar")[-1::-1])

    def test_iter(self):
        self.assertEqual(["f", "o", "o"], list(Path("foo")))
        self.assertIn("foo", Path("foobar"))

    def test_root(self):
        str_path = Path().absolute().get_parent(depth=-1, index=-1).path
        if Path.verInfo.pathRootIsDelimiter:
            self.assertEqual("/", str_path)
        else:
            self.assertTrue(len(str_path) == 3 and str_path[1] == ":" and str_path[2] == Path.path_delimiter)
        self.assertEqual(True, Path().absolute().get_parent(-1, -1).is_root())
        self.assertEqual(False, Path("foo").is_root())
        self.assertEqual(False, Path().absolute().is_root())

    def test_as_working_dir(self):
        working_dir = Path.get_working_dir()
        with Path("hello").as_working_dir():
            self.assertEqual(working_dir / "hello", Path.get_working_dir())

        self.assertEqual(working_dir, Path.get_working_dir())

    def test_match(self):
        self.assertEqual(True, Path("hello/there").match("The*"))
        self.assertEqual(True, Path("hello/there").match("*"))
        self.assertEqual(True, Path("hello/there").match("*h*"))
        self.assertEqual(True, Path(".git").match(".*"))
        self.assertEqual(True, Path(".git").match("."))
        self.assertEqual(True, Path("hello/there").match("The"))
        self.assertEqual(True, Path("hello/there").match("hello/there"))
        self.assertEqual(True, Path("foo/bar/hi").match("/bar/"))
        self.assertEqual(True, Path("foo/bar/hi").match("\\bar\\"))

        self.assertEqual(False, Path("hello/there").match("x"))
        self.assertEqual(False, Path("hello/there").match("*x*"))
        self.assertEqual(False, Path("hello/there").match("there/"))

    def test_encode(self):
        self.assertEqual("foo/bar", Path("foo\\bar").encode())
        self.assertEqual("foo/bar", Path("foo/bar").encode())
        self.assertEqual("foo%20bar", Path("foo bar").encode())
        self.assertEqual("foo/bar/hi%20there", Path("foo/bar\\hi there").encode())
        self.assertEqual("_hello/there_now.py", Path("_hello/there_now.py").encode())
        self.assertEqual("foo/_bar_now", Path("foo\\_bar_now").encode())

    def test_threads(self):
        threads = []
        queue = mp.Queue()
        count = 2
        for i in range(count):
            threads.append(mp.Process(target=_thread_test, args=(queue, i)))
        for thread in threads:
            thread.start()

        results = []
        for i in range(count):
            get = queue.get()
            self.assertNotIn(get, results)
            results.append(get)

        self.assertEqual(len(results), count)

    def test_CaseSensitivityError(self):
        Path("foo.txt").write("hi")
        # Path("foo.txt").get_parent()
        self.assertRaises(CaseSensitivityError, Path("Foo.txt").exists)

    def test_get_alternative_path(self):
        path = Path("foo/bar.txt")
        self.assertEqual(path, path.to_alternative().from_alternative())

        path = path.absolute()
        self.assertEqual(path, path.to_alternative().from_alternative())

    def test_get_cache_dir(self):
        self.assertEqual(True, Path.get_lock_dir().startswith(Path.get_cache_dir()))

    def test_lock(self):
        path = Path("foo.txt")
        with path.lock():
            self.assertEqual(True, path.get_lock_path().exists())

    def test_open_operation(self):
        path = Path("foo.txt")
        with path.lock():
            path.open_operation("w", lambda stream: stream.write("hi"))
            self.assertEqual("hi", path.open_operation("r", lambda stream: stream.read()))

    def test_size(self):
        path = Path("foo.txt")
        path.write("bar")
        self.assertEqual(True, path.size() > 1)

    def test_without_file(self):
        path = Path("foo/bar")
        self.assertEqual("foo/bar", path.without_file())
        path.write()
        self.assertEqual("foo", path.without_file())

    def test_get_differing_files(self):
        Path("one/bar").write("hey")
        Path("one/foo").write("hello")
        Path("two/foo").write("hi")

        for base, target in (("one", "two"), ("two", "one")):
            self.assertEqual({"bar"}, Path(base).get_differing_files(target, exist=True, content=False))
            self.assertEqual({"foo"}, Path(base).get_differing_files(target, exist=False, content=True))
            self.assertEqual({"foo", "bar"}, Path(base).get_differing_files(target, exist=True, content=True))
            self.assertEqual(set(), Path(base).get_differing_files(target, exist=False, content=False))

    def test_contains(self):
        path = Path("foo")
        path.text.write("hello there test")
        self.assertEqual(True, path.contains("there"))
        self.assertEqual(False, path.contains("hi"))

    def test_is_identical(self):
        Path("foo").write("hello")
        Path("bar").write("hello")
        self.assertEqual(True, Path("foo").is_identical("bar"))

        Path("bar").write("hi", overwrite=True)
        self.assertEqual(False, Path("foo").is_identical("bar"))

        Path("foo").write("hi\n", overwrite=True)
        self.assertEqual(False, Path("foo").is_identical("bar"))

    def test_empty(self):
        self.assertEqual(True, Path().empty())
        self.assertEqual(True, Path("new").empty())
        Path("new").create_folder()
        self.assertEqual(True, Path("new").empty())
        Path("new/file.txt").write("foo")
        self.assertEqual(False, Path("new").empty())
        self.assertEqual(False, Path("new/file.txt").empty())
        Path("new/file.txt").delete()
        self.assertEqual(True, Path("new").empty())

    def test_pack(self):
        Path("base/test.txt").write("hello")
        Path("base").pack("target")
        self.assertEqual(True, Path("target.zip").exists())
        Path("target").unpack("new")
        self.assertEqual("hello", Path("new/test.txt").read())

        Path("base").pack("target.tar.gz").unpack("tarnew")
        self.assertEqual("hello", Path("tarnew/test.txt").read())

        Path("base/folder/hi").write("there")
        Path("base").pack("packed/pack.zip").unpack("newbase")
        self.assertEqual("hello", Path("newbase/test.txt").read())
        self.assertEqual("there", Path("newbase/folder/hi").read())

    def test_recycle(self):
        self.assertIs(Path("hi/there"), Path("hi/there"))
        self.assertIs(Path("hi/there")._children, Path("hi/there")._children)
        self.assertIs(Path("hi/there"), Path("hi\\there"))
        self.assertIs(Path("hi/there"), Path("hi") / "there")
        self.assertIs(Path("hi\\there"), Path("hi") / "there")

        self.assertIsNot(Path("hithere"), Path("hi") / "there")
        self.assertIsNot(Path("hi"), Path("hi").absolute())

    def test_read_empty(self):
        with self.assertRaises(FileNotFoundError):
            Path("hey").read()
        self.assertEqual(None, Path("hi").read(default=None))



































