# -*- coding: utf-8 -*-

"""
Create api reference doc.
"""

from __future__ import print_function
try:
    import typing
except:
    pass
import shutil
from pathlib_mate import Path

from .util import make_dir, make_file
from .template import TC
from .pkg.picage import Package, Module


def render_module(module):
    """
    :type module: Module

    :rtype: str
    """
    return TC.module.render(module=module)


def is_ignored(mod_or_pkg, ignored_package):
    """
    Test, if this :class:`docfly.pkg.picage.Module`
    or :class:`docfly.pkg.picage.Package` should be included to generate
    API reference document.

    :param mod_or_pkg: module or package
    :type mod_or_pkg: typing.Union[Module, Package]

    :param ignored_package: ignored package

    **中文文档**

    根据全名判断一个包或者模块是否要被包含到自动生成的API文档中。
    """
    ignored_pattern = list()
    for pkg_fullname in ignored_package:
        if pkg_fullname.endswith(".py"):
            pkg_fullname = pkg_fullname[:-3]
            ignored_pattern.append(pkg_fullname)
        else:
            ignored_pattern.append(pkg_fullname)

    for pattern in ignored_pattern:
        if mod_or_pkg.fullname.startswith(pattern):
            return True
    return False


def render_package(package, ignored_package):
    """
    :param package:
    :type package: Package

    :param ignored_package:
    :type package: list[str]

    :rtype: str
    """
    return TC.package.render(
        package=package,
        ignored_package=ignored_package,
        is_ignored=is_ignored,
    )


class ApiReferenceDoc(object):
    """
    A class to generate sphinx-doc api reference part.

    Example::

        package
        |--- subpackage1
            |--- __init__.rst
            |--- module.rst
        |--- subpackage2
            |--- __init__.rst
            |--- module.rst
        |--- __init__.rst
        |--- module1.rst
        |--- module2.rst

    :param conf_file: the conf.py file for sphinx doc. it helps to locate
        the api reference doc destination directory
    :type conf_file: string

    :param package_name: the importable package name
    :type package_name: string

    :param ignore: default empty list, package, module relative
        prefix you want to ignored
    :type ignored_package: list of string

    **中文文档**

    如果你需要忽略一个包: 请使用 ``docfly.packages``
    如果你需要忽略一个模块: 请使用 ``docfly.zzz_manual_install`` 或
    ``docfly.zzz_manual_install.py``
    """

    def __init__(
        self,
        conf_file,
        package_name,
        ignored_package=None,
    ):
        self.conf_file = conf_file
        self.package = Package(package_name)

        if ignored_package is None:
            ignored_package = list()
        self.ignored_package = list()
        for pkg_fullname in ignored_package:
            if pkg_fullname.endswith(".py"):
                self.ignored_package.append(pkg_fullname[:-3])
            else:
                self.ignored_package.append(pkg_fullname)

    def fly(self):
        """
        Generate doc tree.
        """
        dst_dir = Path(self.conf_file).parent.abspath

        package_dir = Path(dst_dir, self.package.shortname)

        # delete existing api document
        try:
            if package_dir.exists():
                shutil.rmtree(package_dir.abspath)
        except Exception as e:
            print("'%s' can't be removed! Error: %s" % (package_dir, e))

        # create .rst files
        for pkg, parent, sub_packages, sub_modules in self.package.walk():
            if not is_ignored(pkg, self.ignored_package):
                dir_path = Path(*([dst_dir, ] + pkg.fullname.split(".")))
                init_path = Path(dir_path, "__init__.rst")

                make_dir(dir_path.abspath)
                make_file(
                    init_path.abspath,
                    self.generate_package_content(pkg),
                )

                for mod in sub_modules:
                    if not is_ignored(mod, self.ignored_package):
                        module_path = Path(dir_path, mod.shortname + ".rst")
                        make_file(
                            module_path.abspath,
                            self.generate_module_content(mod),
                        )

    def generate_package_content(self, package):
        """Generate package.rst text content.

        ::

            {{ package_name }}
            ==================

            .. automodule:: {{ package_name }}
                :members:

            sub packages and modules
            ------------------------

            .. toctree::
               :maxdepth: 1

                {{ sub_package_name1 }} <{{ sub_package_name1 }}/__init__>
                {{ sub_package_name2 }} <{{ sub_package_name2 }}/__init__>
                {{ sub_module_name1}} <{{ sub_module_name1}}>
                {{ sub_module_name2}} <{{ sub_module_name2}}>

        :type package: Package
        """
        if isinstance(package, Package):
            return render_package(
                package=package,
                ignored_package=self.ignored_package
            )
        else:  # pragma: no cover
            raise Exception("%r is not a Package object" % package)

    def generate_module_content(self, module):
        """Generate module.rst text content.

        ::

            {{ module_name }}
            =================

            .. automodule:: {{ module_fullname }}
                :members:
        """
        if isinstance(module, Module):
            return render_module(module)
        else:  # pragma: no cover
            raise Exception("%r is not a Module object" % module)
