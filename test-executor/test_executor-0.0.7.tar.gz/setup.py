import setuptools

try:
    with open("playlist-creator/README.md", "r") as fh:
        long_description = fh.read()
except Exception:
    with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="test_executor",
    version="0.0.7",
    author="Idan Cohen",
    include_package_data=True,
    author_email="idan57@gmail.com",
    description="This modules allows you to execute tests in the best way possible!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idan57/test_executor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Build Tools',
    ],
    python_requires='>=3.6',
)
