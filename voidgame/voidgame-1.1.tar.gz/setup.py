import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name="voidgame",
	version="1.1",
	author="Joshua Blavatt",
	author_email="josh@joshuablavatt.dev",
	description="A simple interface for a unique game",
	long_description=long_description,
    long_description_content_type="text/markdown",
	url="https://github.com/jpblavatt/voidgame",
	license="MIT",
	python_requires=">=3.8",
	py_modules=["voidgame"],
)