from setuptools import setup


setup(
    name="pyreversi",
    version="0.3.3",
    description="pyreversi is a reversi game in your terminal with IA available.",
    long_description="The complete description/installation/use/FAQ is available at : https://github.com/thib1984/pyreversi#readme",
    url="https://github.com/thib1984/pyreversi",
    author="thib1984",
    author_email="thibault.garcon@gmail.com",
    license="MIT",
    packages=["pyreversi"],
    install_requires=["columnar","click"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "pyreversi=pyreversi.__init__:pyreversi"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
