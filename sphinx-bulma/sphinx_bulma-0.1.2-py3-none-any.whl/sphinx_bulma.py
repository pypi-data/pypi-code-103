import os
from sphinx.util.fileutil import copy_asset_file

def copy_static_files(app, exc):
  if app.builder.format == 'html' and not exc:
    staticdir = os.path.join(app.builder.outdir, '_static')
    curdir = os.path.abspath(os.path.dirname(__file__))
    for directory, _, files in os.walk(os.path.join(curdir, 'static')):
      for file in files:
        copy_asset_file(
          os.path.join(directory, file),
          os.path.join(
            os.path.join(staticdir, os.path.split(directory)[1]),
            file))

def setup(app):
  app.add_html_theme('sphinx-bulma', os.path.abspath(os.path.dirname(__file__)))
  app.connect('builder-inited', copy_static_files)
