import setuptools
import sys


class BinaryDistribution(setuptools.Distribution):
    def has_ext_modules(self):
        return True

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheel(bdist_wheel):
        def run(self):
            clean = self.reinitialize_command('clean')
            clean.all = True
            self.run_command('clean')
            bdist_wheel.run(self)

        def get_tag(self):
            rv = bdist_wheel.get_tag(self)
            l = [self.python_tag, 'none']
            l.extend(rv[2:])
            return tuple(l)

        def finalize_options(self):
            bdist_wheel.finalize_options(self)
            self.root_is_pure = False
except ImportError:
    CustomBdistWheel = None


if sys.platform == "win32":
    is_64bit = sys.maxsize > (2 ** 32)
    if is_64bit:
        package_data = {'hyperborea': ['7zip_64bit/*']}
    else:
        package_data = {'hyperborea': ['7zip_32bit/*']}
    distclass = BinaryDistribution
    cmdclass = {'bdist_wheel': CustomBdistWheel}
else:
    package_data = {}
    distclass = setuptools.Distribution
    cmdclass = {}


def no_local_develop_scheme(version):
    if version.branch == "develop" and not version.dirty:
        return ""
    else:
        from setuptools_scm.version import get_local_node_and_date
        return get_local_node_and_date(version)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="hyperborea",
    use_scm_version={'write_to': 'hyperborea/version.py',
                     'local_scheme': no_local_develop_scheme},
    setup_requires=['setuptools_scm'],
    author="Suprock Technologies, LLC",
    author_email="inquiries@suprocktech.com",
    description="Library for streaming and recording from Asphodel devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/suprocktech/hyperborea",
    packages=setuptools.find_packages(),
    keywords="asphodel suprock apd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.6",
    install_requires=[
        "asphodel",
        "boto3",
        "numpy",
        "psutil",
        "PySide2",
        "requests",
        "setproctitle",
    ],
    zip_safe=False,
    include_package_data=False,
    package_data=package_data,
    distclass=distclass,
    cmdclass=cmdclass,
)
