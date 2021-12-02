from setuptools import setup

setup(
    name="py_elephants",
    packages=["py_elephants"],
    entry_points={
        "console_scripts": [
            "py_elephants = py_elephants.__main__:main",
        ]
    }
)
