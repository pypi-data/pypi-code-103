import os
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


extensions = [
    Extension("FPE.ff1", ["src/FPE/ff1.pyx"]),
    Extension("FPE.ff3", ["src/FPE/ff3.pyx"]),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None

if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)

setup(
    #py_modules = ["FPE/Format","FPE/format_translator","FPE/formatter","FPE/FPE","FPE/fpe_csv","FPE/Mode","FPE/mode_selector"],
    ext_modules=extensions,
    install_requires=["Cython>=0.29.24","numpy>=1.21.4","pycryptodome>=3.11.0"],

)