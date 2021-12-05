import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()


with open("VERSION") as f:
    __version__ = f.read().replace("\n", "")


setuptools.setup(
    name="kafka_processor",
    version=__version__,
    author="Shalom Naim",
    author_email="shalom.naim1@gmail.com",
    description="A package to execute tasks on kafka messages and pass them over",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shalomnaim1/kafka_processor",
    project_urls={
        "Bug Tracker": "https://github.com/shalomnaim1/kafka_processor/issues",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    package_dir={"": "kafka_processor"},
    install_requires=requirements,
    packages=setuptools.find_packages(where="kafka_processor"),
    python_requires=">=3.6"
)
