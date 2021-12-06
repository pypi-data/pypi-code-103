import setuptools
from skbuild import setup
import sys


try:
    from skbuild.command.bdist_wheel import bdist_wheel

    class CustomBdistWheel(bdist_wheel):
        def get_tag(self):
            rv = bdist_wheel.get_tag(self)
            l = [self.python_tag, 'none']
            l.extend(rv[2:])
            return tuple(l)
except ImportError:
    CustomBdistWheel = None


if sys.platform == "win32":
    # download libusb zip, and force use of msvc
    cmake_args = ['-DCMAKE_C_COMPILER=cl.exe', '-DCMAKE_CXX_COMPILER=cl.exe']
    is_64bit = sys.maxsize > (2 ** 32)
    if is_64bit:
        cmake_install_dir = 'asphodel/lib64'
    else:
        cmake_install_dir = 'asphodel/lib32'
else:
    if sys.platform == "darwin":
        cmake_args = ['-DCMAKE_INSTALL_RPATH=@loader_path']
    else:
        cmake_args = ['-DCMAKE_INSTALL_RPATH=$ORIGIN',

                      # limit to 2 parallel jobs for building on raspberry pi
                      '-DCMAKE_JOB_POOL_COMPILE:STRING=compile',
                      '-DCMAKE_JOB_POOL_LINK:STRING=link',
                      '-DCMAKE_JOB_POOLS:STRING=compile=2;link=2']
    cmake_install_dir = 'asphodel/lib'


def no_local_develop_scheme(version):
    if version.branch == "develop" and not version.dirty:
        return ""
    else:
        from setuptools_scm.version import get_local_node_and_date
        return get_local_node_and_date(version)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="asphodel",
    use_scm_version={'write_to': 'asphodel/version.py',
                     'local_scheme': no_local_develop_scheme},
    setup_requires=['setuptools_scm'],
    author="Suprock Technologies, LLC",
    author_email="inquiries@suprocktech.com",
    description="Python wrapper for the Asphodel C library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/suprocktech/asphodel_py",
    packages=setuptools.find_packages(),
    keywords="asphodel suprock",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'nvmeditor = asphodel.nvmeditor:main',
        ],
    },
    zip_safe=False,
    cmake_install_dir=cmake_install_dir,
    cmake_args=cmake_args,
    include_package_data=False,
    exclude_package_data={'asphodel': ['lib*/*.lib', 'lib*/include/*']},
    cmdclass={'bdist_wheel': CustomBdistWheel},
)
