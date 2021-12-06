#!/usr/bin/env python3
import datetime
import distutils.core
import glob
import os.path
import re
import shutil
import subprocess
import sys

import botocore
import cx_Freeze
import PySide2


is_64bit = sys.maxsize > (2 ** 32)

cwd = os.path.abspath(os.path.dirname(__file__))
version = subprocess.check_output([sys.executable, "setup.py", "--version"],
                                  cwd=cwd, universal_newlines=True).strip()

# strip out any part of the version that isn't numeric
version = re.match(r'\d+([.]\d+)*', version).group(0)

if sys.platform == "win32":
    if is_64bit:
        build_key = "win64"
    else:
        build_key = "win32"
else:
    build_key = "unknown"


# use git to find the branch name and commit hash
try:
    branch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], universal_newlines=True,
        cwd=cwd).strip()
    commit = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], universal_newlines=True, cwd=cwd).strip()
except Exception:
    # git probably isn't installed
    branch = ""
    commit = ""
build_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.path.join(cwd, "build_info.txt"), "w", encoding="utf-8") as f:
    f.write("{}\n{}\n{}\n{}\n".format(branch, commit, build_key, build_date))

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

if is_64bit:
    setup_include = ('install_extras/acheron_64bit.iss', 'acheron.iss')
    msvc_include = ('install_extras/msvcp140_64bit.dll', 'msvcp140.dll')
else:
    setup_include = ('install_extras/acheron_32bit.iss', 'acheron.iss')
    msvc_include = ('install_extras/msvcp140_32bit.dll', 'msvcp140.dll')

includefiles = [("build_info.txt", "build_info.txt"),
                ('install_extras/acheron.bmp', 'acheron.bmp'),
                ("acheron/acheron.ico", "acheron.ico"),
                setup_include,
                msvc_include,
                ('LICENSE.txt', 'LICENSE.txt'),
                ('acheron/html', 'html')]

boto_prefix = os.path.abspath(os.path.dirname(botocore.__file__))
boto_includefiles = [
    (boto_prefix + "/cacert.pem", "botodata/cacert.pem"),
    (boto_prefix + "/data/_retry.json", "botodata/_retry.json"),
    (boto_prefix + "/data/endpoints.json", "botodata/endpoints.json"),
    (boto_prefix + "/data/s3", "botodata/s3")]
includefiles.extend(boto_includefiles)

pyside2_prefix = os.path.abspath(os.path.dirname(PySide2.__file__))
pyside2_includefiles = [
    (pyside2_prefix + "/plugins/platforms", "platforms"),
    (pyside2_prefix + "/plugins/styles", "styles"),
    (pyside2_prefix + "/plugins/imageformats/qico.dll",
     "imageformats/qico.dll"),
    (pyside2_prefix + "/plugins/imageformats/qsvg.dll",
     "imageformats/qsvg.dll")]
includefiles.extend(pyside2_includefiles)


includes = ["atexit",  # for QT, not autodetected by cx_freeze
            "configparser", "html.parser",  # boto3
            "boto3.s3", "boto3.s3.inject",  # boto3
            'numpy.core._methods', 'numpy.lib.format',
            'pyqtgraph.debug', 'pyqtgraph.reload', 'pyqtgraph.ThreadsafeTimer',
            'idna', 'idna.idnadata']

excludes = ["pysideuic",  # pulled in by pyqtgraph, not needed
            "matplotlib",
            "scipy",
            'tkinter',
            'firmutil',
            'PySide',
            ]
packages = []


class BdistInnoCommand(distutils.core.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _find_iscc(self):
        paths = []
        program_files_keys = ['PROGRAMW6432', 'PROGRAMFILES',
                              'PROGRAMFILES(X86)']
        program_files_dirs = []
        for key in program_files_keys:
            try:
                path = os.environ[key]
                if path:
                    program_files_dirs.append(path)
            except KeyError:
                pass
        for program_files in program_files_dirs:
            paths.append(os.path.join(program_files, "Inno Setup 6"))
        paths.append(os.environ['PATH'])  # not extend; it's a string
        path = os.pathsep.join(paths)
        return shutil.which("iscc", path=path)

    def run(self):
        build = self.get_finalized_command("build")
        build.run()
        iscc = self._find_iscc()
        if not iscc:
            raise Exception("Could not find ISCC.exe!")

        iss_files = glob.glob(os.path.join(build.build_exe, "*.iss"))
        if not iss_files:
            raise Exception("No iss file in build directory!")
        elif len(iss_files) > 1:
            raise Exception("Too many iss files in build directory!")

        iss_file = iss_files[0]

        dist_dir = "dist"

        subprocess.check_call([iscc, "/DVERSION=" + version, "/O" + dist_dir,
                               iss_file], cwd=cwd)


if sys.platform == "win32":
    cmdclass = {'bdist_inno': BdistInnoCommand}
else:
    cmdclass = {}


cx_Freeze.setup(
    name="acheron",
    version=version,
    author="Suprock Technologies, LLC",
    author_email="inquiries@suprocktech.com",
    description="Plotting and recording program for Asphodel devices",
    options={"build_exe": {"includes": includes,
                           "excludes": excludes,
                           "packages": packages,
                           "include_files": includefiles,
                           "zip_include_packages": ['*'],
                           'zip_exclude_packages': ['numpy', 'asphodel',
                                                    'hyperborea', 'certifi', 'shiboken2', 'pyside2'],
                           "include_msvcr": True,
                           "replace_paths": [("*", "")]}},
    executables=[cx_Freeze.Executable(script="cx_shim_run.py", base=base,
                                      target_name="acheron.exe",
                                      icon="acheron/acheron.ico")],
    cmdclass=cmdclass,
)
