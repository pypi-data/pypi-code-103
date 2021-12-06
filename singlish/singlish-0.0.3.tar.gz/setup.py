import setuptools
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 

with open('README.md', 'r') as fh:
    long_description = fh.read()



setuptools.setup(
    name="singlish",  # Replace with your own username
    version="0.0.3",
    author="asanka9",
    description="A language processing tool for Singlish",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asanka9/singlish",
    packages=setuptools.find_packages(),
    install_requires=[''],
    classifiers=classifiers,
    python_requires='>=3.6'
)