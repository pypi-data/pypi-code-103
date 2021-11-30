import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='jjson2xml',
      version='0.1.1',
      description='Json to XML converter',
      author='Wilson Silva',
      author_email='wilson.silva@bcn.cv',
      license='MIT',
      zip_safe=False,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/bcn-dev/jjson2xml.git",
      package_dir={"": "src"},
      packages=setuptools.find_packages(where="src"),
      python_requires=">=3.6",
      project_urls={
            "Bug Tracker": "https://github.com/bcn-dev/jjson2xml/issues",
      },
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ]
 )