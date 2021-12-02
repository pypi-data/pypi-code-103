# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name="series-de-tiempo-pabloatarama",
      version="2021.12.1",
      author="Pablo Atarama",
      author_email="contacto@pabloatarama.com",
      description="Modelos para el análisis de series de tiempo y proyecciones.",
      long_description=long_description,
      long_description_content_type="text/markdown",      
      url="https://pabloatarama.com/SeriesDeTiempo/",
      packages=["SeriesDeTiempo"],
      )