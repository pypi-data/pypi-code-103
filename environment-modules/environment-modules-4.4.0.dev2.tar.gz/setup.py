#!/usr/bin/env python3
"""# Environment Modules

The Environment Modules package provides for the dynamic modification of a
user's environment via modulefiles.

* Upstream: https://modules.readthedocs.io/en/latest/
* Packaging: https://github.com/bukzor/environment-modules-setuptools
"""
# this really only works on linux systems, at the moment
from __future__ import print_function


from setuptools import setup
from setuptools.command.sdist import sdist as orig_sdist
from setuptools.command.install import install as orig_install
from distutils.core import Command
from distutils.command.build import build as orig_build
from distutils.command.bdist import bdist as orig_bdist


# ############# NOTES #####################
# setuptools.command.sdist.sdist

# setuptools/command/egg_info.py:egg_info.find_sources()
#   seems to be in charge of generating a file list
#   writes SOURCES.txt for its list
#   also reads MANIFEST.in; maybe this is the interface

# setuptools/command/sdist.py:add_defaults
#   adds various files to the file list based on the distribution object

# distutils/command/sdist.py:sdist.make_release_tree(base_dir, files)
#   copy files to base_dir. this will become the sdist


def system(cmd):
    from os import system
    from sys import stderr

    if system("set -ex; " + cmd) != 0:
        exit("command failed: %s" % cmd)


class build(orig_build):
    sub_commands = orig_build.sub_commands + [("build_cexe", None)]


class install(orig_install):
    sub_commands = orig_install.sub_commands + [("install_cexe", None)]


class sdist(orig_sdist):
    def run(self):
        self.run_command("fetch_sources")
        return orig_sdist.run(self)


def repeatable_hash(obj):
    obj = str(obj).encode("latin1")
    import hashlib

    return hashlib.sha1(obj).hexdigest()


class bdist(orig_bdist):
    prefix = None

    def finalize_options(self):
        super(bdist, self).finalize_options()
        self.set_undefined_options("install", ("prefix", "prefix"))
        # append a random number to the "platform" that varies with the install
        # destination; this forces pip to (correctly) not use cached wheels for
        # this package.
        self.plat_name += "-" + repeatable_hash(self.prefix)


class fetch_sources(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        system("./get_sources.sh")


class build_cexe(Command):
    build_temp = None

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
        # self.set_undefined_options('build', ('build_temp', 'build_temp'))

    def run(self):
        self.run_command("fetch_sources")
        # XXX: I wasn't able to figure out how to ./configure this package in a relocatable way.
        # A potential path forward, but requires patches:
        #   * https://www.gnu.org/software/gnulib/manual/html_node/Supporting-Relocation.html
        #   * https://tug.org/pipermail/tex-live/2003-March/003484.html
        #   * http://git.savannah.gnu.org/cgit/gnulib.git/log/?qt=grep&q=relocatable
        # system('./build.sh %s' % self.build_temp)


class install_cexe(Command):
    description = "install C executables"
    outfiles = ()
    build_dir = install_tmp = prefix = None

    def initialize_options(self):
        pass

    def finalize_options(self):
        # this initializes attributes based on other commands' attributes
        self.set_undefined_options("build", ("build_temp", "build_dir"))
        self.set_undefined_options("install", ("install_data", "install_tmp"))
        self.set_undefined_options("install", ("prefix", "prefix"))

    def run(self):
        system(
            "./build.sh '%s' '%s' '%s'"
            % (self.build_dir, self.install_tmp, self.prefix)
        )

    def get_outputs(self):
        return self.outfiles


from wheel.bdist_wheel import bdist_wheel as orig_bdist_wheel


class bdist_wheel(orig_bdist_wheel):
    def get_tag(self):
        # no python implementation
        # no python ABI
        # just platform
        return "none", "none", self.plat_name


command_overrides = {
    "sdist": sdist,
    "bdist": bdist,
    "bdist_wheel": bdist_wheel,
    "fetch_sources": fetch_sources,
    "build": build,
    "build_cexe": build_cexe,
    "install": install,
    "install_cexe": install_cexe,
}


import versions

if versions.version == "master":
    version = "0"
else:
    version = versions.version
version += versions.suffix

setup(
    name="environment-modules",
    long_description=__doc__,
    long_description_content_type="text/markdown",
    version=version,
    cmdclass=command_overrides,
    platforms=["linux"],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: C",
        "Topic :: System",
        "Development Status :: 5 - Production/Stable",
    ],
    options={"bdist_wheel": {"universal": 2}},
)
