#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from os.path import exists, abspath, basename, dirname, normpath, join as pjoin
import argparse
from subprocess import getstatusoutput
import traceback
thisdir = dirname(__file__)
sep = os.sep

BUILD_AUTO_COMMANDS = """
git clone https://github.com/kirin123kirin/.vscode.git
""".strip()

POST_BUILD_AUTO_COMMANDS = """
git init
git add .
git commit -m "first commit(build by initpylib templates.)"
""".strip()

POST_AUTO_MESSAGES = """
git branch -M main
git remote add origin https://github.com/[your user name]/[your repository name].git
git push -u origin main
""".strip()

finishmsg_with_user_operation = f"""
Success `{{targetdir}}` Project Initialize.

if you wan't Git Management.

    cd {{targetdir}}
    {POST_BUILD_AUTO_COMMANDS}
    {POST_AUTO_MESSAGES}

OK Enjoy!
""".format

def command(cmd, quit=False):
    cmd = cmd.strip()
    if not cmd:
        return
    code, dat = getstatusoutput(cmd)
    if code == 0:
        if not quit:
            print(f"Run: {cmd}")
        return dat
    else:
        raise RuntimeError(f"Fail command {cmd}.\nreturn code: {code}\nreturn value:{dat}")
class PJtemplate(object):
    def __init__(self, argv=sys.argv):
        self.argv = argv
        self._args = None
        self.REPLACES_DICT = {}
        self.EXCLUDES = ["build", "dist", ".history", "initpylib.egg-info", "__pycache__", ".egg"]
        self._REPLACES_DICT_B = None

    @property
    def REPLACES_DICT_B(self):
        if not self._REPLACES_DICT_B:
            self._REPLACES_DICT_B = {k.encode(): v.encode() for k, v in self.REPLACES_DICT.items()}
        return self._REPLACES_DICT_B

    def replacer(self, dat):
        for k, v in self.REPLACES_DICT_B.items():
            dat = dat.replace(k, v)
        return dat

    def replacer_first(self, dat):
        for k, v in self.REPLACES_DICT.items():
            return dat.replace(k, v)

    def rencopy_all(self, srcdir, targetdir, add_skip_dirs=[]):
        excludes = self.EXCLUDES + add_skip_dirs
        excludes.sort(key=lambda x: len(x), reverse=True)

        def is_skip(f):
            for e in excludes:
                e = sep + e
                if f.endswith(e) or (e + sep) in f:
                    return True
            return False

        for root, dirs, files in os.walk(srcdir):
            parent = root.replace(srcdir, targetdir)
            if is_skip(parent):
                continue

            for td in dirs:
                if td in excludes:
                    continue

                abstardir = pjoin(parent, td)
                abstardir = self.replacer_first(abstardir)

                if not exists(abstardir):
                    os.mkdir(abstardir)

            for f in files:
                abstarfile = pjoin(parent, f)
                abstarfile = self.replacer_first(abstarfile)
                with open(pjoin(root, f), "rb") as r, open(abstarfile, "wb") as w:
                    w.write(self.replacer(r.read()))

    def run(self):
        a = self.args
        if not exists(a.targetdir):
            os.makedirs(a.targetdir)

        self.rencopy_all(a.common, a.targetdir, [pjoin(a.srcdir, a.pjname)])
        self.rencopy_all(a.srcdir, a.targetdir)

        os.chdir(a.targetdir)
        for cmd in BUILD_AUTO_COMMANDS.splitlines():
            command(cmd, self.args.quit)

        if a.with_git_init:
            for cmd in POST_BUILD_AUTO_COMMANDS.splitlines():
                command(cmd, self.args.quit)
            if not a.quit:
                print("Finished git initialize.")
        else:
            if not a.quit:
                print(finishmsg_with_user_operation(targetdir=a.targetdir))

    @property
    def args(self):
        if self._args is None:
            ps = argparse.ArgumentParser(
                description='Build Python Some Project Template.',
                prog="initpy"
            )

            subps = ps.add_subparsers()

            def add_subcmd(subcmdname, help):
                subps_args = subps.add_parser(subcmdname, help=help)
                subps_args.set_defaults(template="templates_" + ("common" if subcmdname == "py" else subcmdname))
                subps_args.add_argument("new_projectpath", type=normpath,
                                        help="Build New Project Directory Path(default build in current directory)")

            add_subcmd("capi", "Build Python C/C++ Extension API Module Project")
            add_subcmd("py", "Build Pure Python Module Project")

            ps.add_argument("-g", "--with_git_init", action="store_true",
                            help="build with git init & commit (default False)")
            ps.add_argument("-q", "--quit", action="store_true",
                            help="stdout print quit mode. (default False)")

            self._args = ps.parse_args(self.argv[1:])

            if hasattr(self._args, 'template'):
                srcdir = abspath(pjoin(thisdir, self._args.template))
                common = abspath(pjoin(thisdir, "templates_common"))
                if not exists(srcdir):
                    raise RuntimeError("Error exists Any Bugs.\nWhere Source Directory" + srcdir)
            else:
                ps.print_help()
                sys.exit(1)

            targetdir = abspath(self._args.new_projectpath)
            pjname = basename(targetdir)

            global REPLACES_DICT
            self.REPLACES_DICT.update({
                "_PLEASE_PYPROJECT_NAME_": pjname,
                "_PLEASE_EXECUTABLE_FILENAME_": pjname + ".exe" if os.name == "nt" else pjname,
            })

            self._args.pjname = pjname
            self._args.common = common
            self._args.srcdir = srcdir
            self._args.targetdir = targetdir

        return self._args

def main(argv=sys.argv):
    orgdir = abspath(os.getcwd())
    try:
        PJtemplate(argv).run()
    except Exception:
        traceback.print_exc(file=sys.stderr)
    finally:
        os.chdir(orgdir)


if __name__ == "__main__":
    main()
