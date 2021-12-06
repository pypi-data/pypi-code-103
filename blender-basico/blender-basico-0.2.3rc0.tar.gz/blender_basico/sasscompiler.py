"""Blender-basico's Libsass compiler for django-pipeline.

It's just like https://github.com/sonic182/libsasscompiler,
but allows compiling SASS that imports Basico's SASS from other apps' static,
adding a custom `COMPILERS_INCLUDED_APP_STATIC` `PIPELINE` setting.

Why not use django-pipeline's `compiler_options`, you might ask?
That is because these only get passed on `collectstatic`,
while we need our compilation pipeline to work the same way
with both DEBUG == True and DEBUG == False.

See relevant issue:
https://github.com/jazzband/django-pipeline/issues/112#issuecomment-5884050
"""
import logging
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from pipeline.compilers import CompilerBase
import codecs
import sass
logger = logging.getLogger(__name__)


class LibSassCompilerWithAppStatic(CompilerBase):
    """Compiler that uses libsass and includes static dirs of multiple apps.

    Use COMPILERS_INCLUDED_APP_STATIC in settings.PIPELINE to list apps,
    static directories of which must be included during compilation.
    """

    output_extension = 'css'

    def _get_include_paths(self):
        include_paths = set()
        for path in settings.PIPELINE.get('COMPILERS_INCLUDED_APP_STATIC', []):
            result = finders.find(path)
            if not result:
                logger.error('Unable to find %s', path)
                continue
            include_paths.add(os.path.dirname(result))
        return include_paths

    def match_file(self, filename):
        """Check files extension to use them."""
        return filename.endswith(('.scss', '.sass'))

    def compile_file(self, infile, outfile, outdated=False, force=False):
        """Process sass file."""
        include_paths = self._get_include_paths()

        myfile = codecs.open(outfile, 'w', 'utf-8')

        if settings.DEBUG:
            myfile.write(sass.compile(filename=infile,
                                      include_paths=include_paths))
        else:
            myfile.write(sass.compile(filename=infile,
                                      output_style='compressed',
                                      include_paths=include_paths))
        return myfile.close()
