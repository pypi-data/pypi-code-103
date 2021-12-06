import os
import pathlib
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist
from distutils.dir_util import mkpath

# this directory
#PYDIR = os.path.dirname(os.path.realpath(pathlib.Path(__file__)))
# read in the Python module README markdown file
with open(os.path.join('python', 'README.md'), 'r') as readme:
    README = readme.read()

# the directory for the lexer/parser source
parser_dir = os.path.join('gensrc', 'parser')
# the source files for the lexer and parser
lexer_src = os.path.join(parser_dir, 'dsl.yy.c')
parser_src = os.path.join(parser_dir, 'dsl.tab.c')

nfer_c_extension = Extension('_nfer',
                    include_dirs = ['inc', parser_dir],
                    sources = [
                        os.path.join('src', 'types.c'),
                        os.path.join('src', 'log.c'),
                        os.path.join('src', 'nfer.c'),
                        os.path.join('src', 'dict.c'),
                        os.path.join('src', 'pool.c'),
                        os.path.join('src', 'file.c'),
                        os.path.join('src', 'map.c'),
                        os.path.join('src', 'stack.c'),
                        os.path.join('src', 'expression.c'),
                        os.path.join('src', 'ast.c'),
                        os.path.join('src', 'semantic.c'),
                        os.path.join('src', 'generate.c'),
                        os.path.join('src', 'astutil.c'),
                        os.path.join('src', 'memory.c'),
                        os.path.join('src', 'strings.c'),
                        os.path.join('src', 'learn.c'),
                        os.path.join('src', 'pyinterface.c'),
                        lexer_src, parser_src
                        ])

def generate_lexer_parser_source():
    "Checks for the lexer and parser source files and generates them if they are missing or outdated"

    # check if the parser source dir exists at all and create it if not
    if not os.path.exists(parser_dir):
        # using the distutils helper
        mkpath(parser_dir)

    # check for the lexer source and create it if it doesn't exist or is outdated
    lexer_l = os.path.join('src', 'dsl.l')
    lexer_src_is_old = True
    if os.path.exists(lexer_src) and os.path.exists(lexer_l):
        lexer_src_is_old = os.path.getmtime(lexer_src) < os.path.getmtime(lexer_l)
    
    if lexer_src_is_old:
        print('running flex')
        os.system('flex -o ' + lexer_src + ' ' + lexer_l)

    # check for the parser source and create it if it doesn't exist or is outdated
    parser_y = os.path.join('src', 'dsl.y')
    parser_src_is_old = True
    if os.path.exists(parser_src) and os.path.exists(parser_y):
        parser_src_is_old = os.path.getmtime(parser_src) < os.path.getmtime(parser_y)

    if parser_src_is_old:
        print('running bison')
        os.system('bison -d -o ' + parser_src + ' ' + parser_y)


class NferBuildPy(build_ext):
    def run(self):
        "overriding the build_ext command called by install to ensure the lexer/parser source exists"

        # honor the --dry-run flag
        if not self.dry_run:
            generate_lexer_parser_source()

        # call the super class method
        return build_ext.run(self)

class NferSourceDist(sdist):
    # you can override the behavior of any setuptools command this way
    def run(self):
        "Run preprocessor commands when building the source dist so installers don't need these dependencies."

        # honor the --dry-run flag
        if not self.dry_run:
            generate_lexer_parser_source()

        # call the super class method
        return sdist.run(self)


setup (name = 'NferModule',
       version = '0.10.0',
       description = 'The nfer language for Python',
       long_description = README,
       long_description_content_type = 'text/markdown',
       author = 'Sean Kauffman',
       author_email = 'skauffma@uwaterloo.ca',
       url = 'http://nfer.io/',
       package_dir = {'nfer': os.path.join('python', 'nfer')},
       packages = ['nfer'],
       ext_modules = [nfer_c_extension],
       cmdclass={'build_ext': NferBuildPy, 'sdist': NferSourceDist},
       install_requires=['aiohttp[speedups]', 'python-socketio>=5'],
       python_requires='>=3.5',
       include_package_data=True,
       zip_safe=False)

