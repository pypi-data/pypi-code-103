from setuptools import setup


def readme():
    with open("README.rst", mode="r", encoding="utf-8") as f:
        return f.read()


setup(name="pprl",
      version="0.1.3",
      description="Client utilities for the MDS PPRL services",
      long_description=readme(),
      url="https://hub.docker.com/mds4ul",
      author="Maximilian Jugl",
      author_email="jugl@hs-mittweida.de",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Software Development :: Libraries",
          "Typing :: Typed"
      ],
      license="GPL-3.0-or-later",
      packages=["pprl", "pprl.broker", "pprl.encoder", "pprl.match", "pprl.resolver"],
      install_requires=[
          "requests"
      ],
      zip_safe=False)
