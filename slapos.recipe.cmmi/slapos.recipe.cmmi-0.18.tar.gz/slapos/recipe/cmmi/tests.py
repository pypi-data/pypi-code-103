from slapos.recipe.downloadunpacked import Signature
from zope.testing import renormalizing
import doctest
import errno
import os
import re
import shutil
import stat
import tarfile
import tempfile
from contextlib import contextmanager
from io import BytesIO
from time import sleep
import pkg_resources
import zc.buildout
import zc.buildout.testing
import zc.buildout.tests

try:
    import unittest2 as unittest
except ImportError:
    import unittest

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    os.environ.pop('MAKEFLAGS', None)
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('slapos.recipe.build', test)
    zc.buildout.testing.install_develop('slapos.recipe.cmmi', test)

def tarfile_addfileobj(tarobj, name, dataobj, **kw):
    tarinfo = tarfile.TarInfo(name)
    dataobj.seek(0, 2)
    tarinfo.size = dataobj.tell()
    dataobj.seek(0)
    for x in kw.items():
        setattr(tarinfo, *x)
    tarobj.addfile(tarinfo, dataobj)

@contextmanager
def fake_package(**kw):
    with tempfile.NamedTemporaryFile(suffix=".tar") as tmp:
        with tarfile.open(mode='w', fileobj=tmp) as tar:
            for k, v in kw.items():
                tarfile_addfileobj(tar, k, BytesIO(v.encode()),
                    **{'mode':stat.S_IRWXU} if v.startswith('#!') else {})
        tmp.flush()
        yield tmp.name

class NonInformativeTests(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.realpath(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)
        for var in list(os.environ.keys()):
            if var.startswith('HRC_'):
                del os.environ[var]

    def write_file(self, filename, contents, mode=stat.S_IREAD | stat.S_IWUSR):
        path = os.path.join(self.dir, filename)
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
        os.chmod(path, mode)
        return path

    def make_recipe(self, buildout, name, options, **buildout_options):
        from slapos.recipe.cmmi import Recipe
        parts_directory_path = os.path.join(self.dir, 'test_parts')
        try:
            os.mkdir(parts_directory_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        bo = {
            'buildout': {
                'parts-directory': parts_directory_path,
                'directory': self.dir,
            }
        }
        bo.update(buildout)
        bo['buildout'].update(buildout_options)
        return Recipe(bo, name, options)

    def test_working_directory_restored_after_failure(self):
        compile_directory = os.path.join(self.dir, 'compile_directory')
        os.makedirs(compile_directory)
        recipe = self.make_recipe({}, 'test', {'path': compile_directory})
        os.chdir(self.dir)

        with self.assertRaises(zc.buildout.UserError):
            recipe.install()
        self.assertEqual(self.dir, os.getcwd())

    def test_working_directory_restored_after_success(self):
        compile_directory = os.path.join(self.dir, 'compile_directory')
        os.makedirs(compile_directory)
        self.write_file(os.path.join(compile_directory, 'configure'), 'Dummy configure')

        self.make_recipe({}, 'test', {'path': compile_directory})
        os.chdir(self.dir)
        self.assertEqual(self.dir, os.getcwd())

    def test_restart_after_failure(self):
        with fake_package(
                configure='#!/bin/sh\n',
                Makefile='all:\n\texit -1',
                ) as tarfile_path:
            recipe = self.make_recipe({}, 'test', {'url': tarfile_path})
            os.chdir(self.dir)

            # expected failure
            with self.assertRaises(zc.buildout.UserError):
                recipe.install()

            # the install should still fail, and _not_ raise an OSError
            with self.assertRaises(zc.buildout.UserError):
                recipe.install()

    def test_environment_restored_after_building_a_part(self):
        # Make sure the test variables do not exist beforehand
        self.assertFalse('HRC_FOO' in os.environ)
        self.assertFalse('HRC_BAR' in os.environ)
        # Place a sentinel value to make sure the original environment is
        # maintained
        os.environ['HRC_SENTINEL'] = 'sentinel'
        self.assertEqual(os.environ.get('HRC_SENTINEL'), 'sentinel')

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'environment': 'HRC_FOO=bar\nHRC_BAR=foo'})
        os.chdir(self.dir)
        recipe.install()

        # Make sure the test variables are not kept in the environment after
        # the part has been built.
        self.assertFalse('HRC_FOO' in os.environ)
        self.assertFalse('HRC_BAR' in os.environ)
        # Make sure the sentinel value is still in the environment
        self.assertEqual(os.environ.get('HRC_SENTINEL'), 'sentinel')

    def test_run__unknown_command(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__)})
        with self.assertRaises(zc.buildout.UserError):
            recipe.run('this-command-does-not-exist')

    def test_strip_top_dir_control(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'keep-compile-dir': 'true'})
        os.chdir(self.dir)
        recipe.install()
        self.assertTrue(os.path.exists('test_parts/test/.build/package-0.0.0'))

    def test_strip_top_dir(self):
        recipe = self.make_recipe({}, 'test', { 
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'keep-compile-dir': 'true',
            'strip-top-level-dir': 'true'})
        os.chdir(self.dir)
        recipe.install()
        self.assertTrue(os.path.exists('test_parts/test/.build/configure'))

    def test_stop_shell_on_error_midway(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
        })
        recipe.run('true \n true \n true')
        with self.assertRaises(zc.buildout.UserError):
            recipe.run('true \n false \n true')

    def test_call_script__bbb_for_callable_with_two_parameters(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
        })

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        filename = os.path.join(self.dir, 'hooks.py')
        script = open(filename, 'w')
        script.write('def my_hook(options, buildout): raise ValueError("I got called")\n')
        script.close()

        try:
            recipe.call_script('%s:my_hook' % filename)
            self.fail("The hook script was not called.")
        except ValueError as e:
            self.assertEqual(str(e), 'I got called')

    def test_call_script__augmented_environment_as_third_parameter(self):
        os.environ['HRC_SENTINEL'] = 'sentinel'
        os.environ['HRC_TESTVAR'] = 'foo'

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'environment': 'HRC_TESTVAR=bar'
        })

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        filename = os.path.join(self.dir, 'hooks.py')
        script = open(filename, 'w')
        script.write('def my_hook(options, buildout, env): raise ValueError("%(HRC_SENTINEL)s %(HRC_TESTVAR)s" % env)\n')
        script.close()

        try:
            recipe.call_script('%s:my_hook' % filename)
            self.fail("The hook script was not called.")
        except ValueError as e:
            self.assertEqual(str(e), 'sentinel bar')

    def no_test_make_target_with_prefix(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'configure-command' : './configure',
            'pre-install' : 'sed -i -e "s/installing package/installing package at \$\$prefix /g" Makefile',
            })
        os.chdir(self.dir)
        recipe.install()

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'pre-install' : 'sed -i -e "s/installing package/installing package at \$\$prefix /g" Makefile',
            'make-targets' : 'install-lib prefix=%(prefix)s',
            })
        recipe.install()

    def test_download_file(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            })
        url = '%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__)
        file, is_temp = recipe.download_file(url)
        self.assertFalse(is_temp)
        self.assertEqual(file, url)

        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)

        with open(os.path.join(tmpdir, 'hello.txt'), 'w') as f:
            f.write('Hello\n')
        # This file md5sum is 09f7e02f1290be211da707a266f153b3

        port = zc.buildout.testing.start_server(tmpdir)

        url = 'http://localhost:%s/hello.txt' % port
        file, is_temp = recipe.download_file(url)
        self.assertTrue(is_temp)
        self.assertTrue(os.path.exists(file))

        url = 'http://localhost:%s/hello.txt#09f7e02f1290be211da707a266f153b3' % port
        file, is_temp = recipe.download_file(url)
        self.assertTrue(is_temp)
        self.assertTrue(os.path.exists(file))

        url = 'http://localhost:%s/hello.txt#0205' % port
        self.assertRaises(zc.buildout.download.ChecksumError, recipe.download_file, url)

    def test_buildout_prefix(self):
        buildout_prefix = os.path.join(self.dir, 'test_parts/test_local')
        os.makedirs(buildout_prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            },
            prefix=buildout_prefix
            )
        self.assertEqual(recipe.options.get('prefix'), buildout_prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'prefix' : self.dir,
            },
            prefix=buildout_prefix
            )
        self.assertEqual(recipe.options.get('prefix'), self.dir)

    def test_get_installed_files(self):
        prefix = os.path.join(self.dir, 'test_parts/test_local')
        os.makedirs(prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            })
        os.chdir(self.dir)

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        no_installed_files = ('a.txt', 'b.txt', 'c', 'c/d.txt')
        installed_files = ['e.txt', 'f.txt', 'g', 'g/h.txt']
        for s in no_installed_files:
            if s.endswith('.txt'):
                f = open(os.path.join(prefix, s), 'w')
                f.write(s)
                f.close()
            else:
                os.makedirs(os.path.join(prefix, s))
        sleep(2)
        ref_path = os.path.join(self.dir, 'refs')
        os.makedirs(ref_path)
        sleep(2)
        for s in installed_files:
            if s.endswith('.txt'):
                f = open(os.path.join(prefix, s), 'w')
                f.write(s)
                f.close()
            else:
                os.makedirs(os.path.join(prefix, s))
        recipe.buildout_prefix = prefix
        file_list = recipe.get_installed_files(ref_path)
        installed_files.pop(2)
        self.assertEqual(set(os.path.relpath(f, prefix) for f in file_list),
                         set(installed_files))

    def test_honor_buidlout_keep_compile_directory(self):
        buildout = {'keep-compile-dir' : 'true'}
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            },
            **buildout
            )
        os.chdir(self.dir)
        recipe.install()

        build_directory = os.path.join(self.dir, 'test_parts/test/.build')
        self.assertTrue(os.path.exists(build_directory))

    def test_bad_symlink_in_bin(self):
        with fake_package(
                configure="""#!/bin/sh
echo prefix = ${@##--prefix=} > Makefile.in
""",
                Makefile="""include Makefile.in
install:
\tmkdir -p $(prefix)/bin
\tln -sf /DUMMYFILENOTEXISTING $(prefix)/bin/badlink
""",
                ) as tarfile_path:
            recipe = self.make_recipe({}, 'test', {'url': tarfile_path})
            os.chdir(self.dir)
            recipe.install()
            self.assertTrue(os.path.islink('test_parts/test/bin/badlink'))

def test_suite():
    sums = []
    def md5sum(m):
        x = m.group(0)
        try:
            i = sums.index(x)
        except ValueError:
            i = len(sums)
            sums.append(x)
        return '<MD5SUM:%s>' % i

    def _reset_md5sums():
      del sums[:]

    doctest_files = ['README.rst']
    if 'slapos' in pkg_resources.working_set.find(
        pkg_resources.Requirement.parse('zc.buildout')).version:
      doctest_files += ['README-SlapOS.rst']

    tests = [
      doctest.DocFileSuite(
            filename,
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                (re.compile(r'--prefix=\S+sample-buildout'),
                 '--prefix=/sample_buildout'),
                (re.compile(r'\s/\S+sample-buildout'),
                 ' /sample_buildout'),
                (re.compile(r'--prefix=\S+\/shared\/'),
                 '--prefix=/shared/'),
               (re.compile(r'\s/\S+\/shared\/'),
                 ' /shared/'),
               (re.compile(
                 r'.*CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. '
                 'Support for it is now deprecated in cryptography, and will be removed in the next release.\n.*'), ''),
               (re.compile('[0-9a-f]{32}'), md5sum),
                # Normalize subprocess.CalledProcessError message, on python >= 3.6
                # there's an extra . at the end.
               (re.compile(r'Command (.*) returned non-zero exit status (\d+)[\.]{0,1}'),
                  r'Command \1 returned non-zero exit status \2.'),
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.not_found,
            ]),
            globs={'_reset_md5sums': _reset_md5sums},
      ) for filename in doctest_files] + [
         unittest.makeSuite(NonInformativeTests)
        ]
    suite = unittest.TestSuite(tests)
    return suite


def load_tests(*args):
  return test_suite()
