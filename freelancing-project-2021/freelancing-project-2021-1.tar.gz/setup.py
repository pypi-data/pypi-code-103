import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="freelancing-project-2021",
    version="1",
    author="Abdallah Ziad",
    author_email="boodyziad1@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={
        'freelancing-project-2021': [
                '*.html',
                '*.css'
                'src/NOWNT/templates/index.html',
                'src/NOWNT/templates/base.html',
                'src/NOWNT/templates/previous.html',
                'src/NOWNT/templates/results.html',
                'src/NOWNT/static/styles/styles.css'
            ]
        },
    include_package_data=True,
    install_requires=install_requires
)
