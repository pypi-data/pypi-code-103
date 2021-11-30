import errno
import imp
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import zc.buildout
from zc.buildout import UserError
from zc.buildout.buildout import bool_option
from .. import (
  # from slapos.recipe.build
  EnvironMixin, Shared, downloadunpacked, is_true, rmtree
)

startup_environ = os.environ.copy()

# backport of shlex.quote from Python 3.3
_find_unsafe = re.compile(r'[^\w@%+=:,./-]', 256).search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"
###

class Recipe(EnvironMixin):
    """zc.buildout recipe for compiling and installing software"""

    buildout_prefix = ''
    _shared = None

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        shared = Shared(buildout, name, options)
        # It was never possible to choose location. It is sometimes set by the
        # user when the value is needed before __init__ is called: in such
        # case, the value must be the same as what Shared computes. However,
        # the user should use %(location)s when possible.
        location = options.get('location')
        if location is not None and shared.location != location.replace(
                '@@LOCATION@@', shared.location):
            raise UserError("invalid 'location' value")
        location = options['location'] = shared.location

        prefix = options.get('prefix')
        if prefix:
            prefix = prefix.replace('@@LOCATION@@', location)
            if os.path.commonprefix((prefix, location)) != location:
                shared.assertNotShared("'prefix' can't be outside location")
        else:
            prefix = buildout['buildout'].get('prefix') # XXX: buggy
            if prefix:
                # XXX: one issue is that a change of ${buildout:prefix}
                #      does not cause a reinstallation of the part
                shared.assertNotShared(
                    "option 'prefix' must be set"
                    " or ${buildout:prefix} can't be set")
                shared = None
                if 'cygwin' == sys.platform: # XXX: why?
                    self.buildout_prefix = prefix
                options['prefix'] = prefix
            else:
                options['prefix'] = location
        if shared:
            shared.keep_on_error = True
            self._shared = shared

        url = options.get('url')
        path = options.get('path')
        if url:
            if path:
                raise UserError('You must provide either "url" or "path".')
            options['compile-directory'] = os.path.join(location, '.build')
        elif path:
            options['compile-directory'] = path
        else:
            raise UserError('You must use either "url" or "path", not both!')

        for k, v in list(options.items()):
            if '@@LOCATION@@' in v:
                options[k] = v.replace('@@LOCATION@@', location)

        EnvironMixin.__init__(self, False)

    def update(self):
        pass

    def download_file(self, url):
        download = zc.buildout.download.Download(
          self.buildout['buildout'], hash_name=True)
        url, _s_, md5sum = url.partition('#')
        return download(url, md5sum=md5sum or None)

    def get_installed_files(self, ref_file):
        # if [buildout] has option 'prefix', then return all the files
        # in this path which create time is newer than ref_file.
        # Exclude directory and don't follow link.
        return subprocess.check_output((
            'find', self.buildout_prefix,
            '-cnewer', ref_file, '!', '-type', 'd',
            ), universal_newlines=True, close_fds=True).splitlines()

    def check_promises(self):
        result = True
        for path in self.options.get('promises', '').splitlines():
            if path and not os.path.exists(path):
                result = False
                self.logger.warning('could not find promise %r', path)
        return result

    def call_script(self, script):
        """This method is copied from z3c.recipe.runscript.

        See http://pypi.python.org/pypi/z3c.recipe.runscript for details.
        """
        url, callable = script.rsplit(':', 1)
        filename, is_temp = self.download_file(url)
        try:
            if not is_temp:
                filename = os.path.abspath(filename)
            module = imp.load_source('script', filename)
            script = getattr(module, callable.strip())
            try:
                script(self.options, self.buildout, self.environ)
            except TypeError:
                # BBB: Support hook scripts that do not take the environment as
                # the third parameter
                script(self.options, self.buildout)
        finally:
            if is_temp:
                os.remove(filename)

    def run(self, cmd):
        """Run the given ``cmd`` in a child process."""
        try:
            subprocess.check_call('set -e;' + cmd, shell=True,
                env=self.environ, close_fds=True)
        except Exception as e:
            self.logger.error(e)
            raise UserError('System error')

    def install(self):
        shared = self._shared
        if shared:
          return shared.install(self._install)
        location = self.options['location']
        rmtree(location)
        os.makedirs(location)
        return self._install()

    def _install(self):
        log = self.logger
        parts = []

        # Add prefix to PATH, CPPFLAGS, CFLAGS, CXXFLAGS, LDFLAGS
        if self.buildout_prefix:
            self.environ['PATH'] = '%s/bin:%s' % (self.buildout_prefix, self.environ.get('PATH', '/usr/bin'))
            self.environ['CPPFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CPPFLAGS', ''))
            self.environ['CFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CFLAGS', ''))
            self.environ['CXXFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CXXFLAGS', ''))
            self.environ['LDFLAGS'] = '-L%s/lib %s' % (self.buildout_prefix, self.environ.get('LDFLAGS', ''))

        make_cmd = self.options.get('make-binary', 'make').strip()
        make_options = ' '.join(self.options.get('make-options', '').split())
        make_targets = ' '.join(self.options.get('make-targets', 'install').split())

        configure_options = self.options.get('configure-options', '').split()
        configure_cmd = self.options.get('configure-command', '').strip()

        if configure_cmd == 'cygport':
            self.environ.setdefault('CYGCONF_PREFIX', self.options['prefix'])

        if not configure_cmd:
            # Default to using basic configure script.
            configure_cmd = './configure'
            # Inject the --prefix parameter if not already present
            if '--prefix' not in ' '.join(configure_options):
                configure_options.insert(0, '--prefix=\"%s\"' % self.options['prefix'])
        elif make_cmd == 'make' and make_targets == 'install':
            make_targets += ' prefix=\"%s\"' % self.options['prefix']

        configure_cmd = '%s %s' % (configure_cmd, ' '.join(configure_options)) % self.options
        install_cmd = '%s %s %s' % (make_cmd, make_options, make_targets) % self.options
        make_cmd = '%s %s' % (make_cmd, make_options) % self.options

        patch_cmd = self.options.get('patch-binary', 'patch').strip()
        patch_options = ' '.join(self.options.get('patch-options', '-p0').split())
        patches = self.options.get('patches', '').split()

        current_dir = os.getcwd()
        url = self.options.get('url')
        compile_dir = self.options['compile-directory']
        location = self.options['location']
        parts = [location]
        # Download the source using slapos.recipe.downloadunpacked
        if url:
            os.mkdir(compile_dir)
            self.options.get('md5sum') # so that buildout does not complain "unused option md5sum"
            opt = self.options.copy()
            opt['destination'] = compile_dir
            # no need to shared build for compile dir
            opt['shared'] = 'false'
            opt['strip-top-level-dir'] = opt.get(
                'strip-top-level-dir') or 'false'
            downloadunpacked.Recipe(self.buildout, self.name, opt).install()
        else:
            log.info('Using local source directory: %s', compile_dir)
        try:
            os.chdir(compile_dir)
            try:
                # We support packages that either extract contents to the $PWD
                # or alternatively have a single directory.
                contents = os.listdir('.')
                if len(contents) == 1 and os.path.isdir(contents[0]):
                    # Single container
                    os.chdir(contents[0])

                if patches:
                    log.info('Applying patches')
                    for patch in patches:
                        patch_filename, is_temp = self.download_file(patch)
                        try:
                            self.run('%s %s < %s' % (patch_cmd, patch_options,
                                                     patch_filename))
                        finally:
                            if is_temp:
                                os.remove(patch_filename)

                if 'pre-configure-hook' in self.options and len(self.options['pre-configure-hook'].strip()) > 0:
                    log.info('Executing pre-configure-hook')
                    self.call_script(self.options['pre-configure-hook'])

                pre_configure_cmd = self.options.get('pre-configure', '').strip() % self.options
                if pre_configure_cmd != '':
                    log.info('Executing pre-configure')
                    self.run(pre_configure_cmd)

                self.run(configure_cmd)

                if 'pre-make-hook' in self.options and len(self.options['pre-make-hook'].strip()) > 0:
                    log.info('Executing pre-make-hook')
                    self.call_script(self.options['pre-make-hook'])

                pre_build_cmd = self.options.get('pre-build', '').strip() % self.options
                if pre_build_cmd != '':
                    log.info('Executing pre-build')
                    self.run(pre_build_cmd)

                self.run(make_cmd)

                pre_install_cmd = self.options.get('pre-install', '').strip() % self.options
                if pre_install_cmd != '':
                    log.info('Executing pre-install')
                    self.run(pre_install_cmd)

                self.run(install_cmd)

                if 'post-make-hook' in self.options and len(self.options['post-make-hook'].strip()) > 0:
                    log.info('Executing post-make-hook')
                    self.call_script(self.options['post-make-hook'])

                post_install_cmd = self.options.get('post-install', '').strip() % self.options
                if post_install_cmd != '':
                    log.info('Executing post-install')
                    self.run(post_install_cmd)
                if (self.buildout_prefix
                        and os.path.exists(self.buildout_prefix)):
                    log.info('Getting installed file lists')
                    parts += self.get_installed_files(compile_dir)
            except:

                with open('slapos.recipe.build.env.sh', 'w') as env_script:
                    for key, v in sorted(self.environ.items()):
                        if v != startup_environ.get(key):
                            env_script.write('%sexport %s=%s\n' % (
                                '#'[:key in ('TEMP', 'TMP', 'TMPDIR')],
                                key, quote(v)))
                    env_script.write('''\
echo "If this recipe does not use pre/post hooks or commands, you can re-run as below."
echo configure with:
echo %s
echo
echo make with:
echo %s
echo
echo install with:
echo %s
''' % (quote("  " + configure_cmd), quote("  " + make_cmd), quote("  " + install_cmd)))

                log.error('Compilation error. The package is left as is at %s where '
                          'you can inspect what went wrong.\n'
                          'A shell script slapos.recipe.build.env.sh has been generated. '
                          'You can source it in your shell to reproduce build environment.',
                          os.getcwd())

                raise
        finally:
            os.chdir(current_dir)

        if url and not is_true(
                self.options.get('keep-compile-dir') or
                self.buildout['buildout'].get('keep-compile-dir')):
            shutil.rmtree(compile_dir)

        # Check promises
        self.check_promises()

        self.fix_shebang(location)
        return parts

    def fix_shebang(self, location):
        # Workaround for shebang line limit by renaming the script and
        # putting a wrapper shell script.
        for dir in ('bin', 'sbin'):
            dir_abspath = os.path.join(location, dir)
            if not os.path.isdir(dir_abspath):
                continue
            for f in os.listdir(dir_abspath):
                f_abspath = os.path.join(dir_abspath, f)
                st_mode = os.lstat(f_abspath).st_mode
                if not stat.S_ISREG(st_mode):
                    continue
                with open(f_abspath, 'rb') as f:
                    header = f.readline(128)
                if header.startswith(b'#!') and header[-1] != b'\n':
                    os.rename(f_abspath, f_abspath + '.shebang')
                    with open(f_abspath, 'w') as f:
                        os.fchmod(f.fileno(), stat.S_IMODE(st_mode))
                        f.write('''#!/bin/sh -e
read -r EXE ARG < "$0.shebang"
EXE=${EXE#\\#!}
[ "$EXE" ] || read -r _ EXE ARG < "$0.shebang"
exec $EXE ${ARG:+"$ARG"} "$0.shebang" "$@"
''')
