from distutils.core import setup
from os import path
import pathlib


root_dir = pathlib.Path(__file__).parent
with open(path.join(root_dir, 'requirements.txt')) as requirements_file:
    all_lines = requirements_file.read().split('\n')
    all_requirements = [r.strip() for r in all_lines]

setup(
    name="latexsuite",
    version="0.9.1",
    description="Support your bash needs when working with latex projects in git repositories.",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/jbuerman/latexsuite",
    author="Jan Buermann",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    packages=["latex_suite"],
    include_package_data=True,
    install_requires=all_requirements,
    entry_points={"console_scripts": ["latexsuite=latex_suite.latex_suite:main"]},
)
