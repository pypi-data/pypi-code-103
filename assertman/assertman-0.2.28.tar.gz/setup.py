from setuptools import find_packages, setup

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name="assertman",
    version="0.2.28",
    # author="Maxim Kuznetsov",
    # author_email="7473233@gmail.com",
    # description="A utility package for making better test assertions in api tests",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="https://github.com/lunjon/asserty",
    packages=find_packages(),
    # package_dir={"": "cerberus_matchers"},
    # package_data={"cerberus_matchers": ["py.typed"]},
    # py_modules=['library'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['cerberus', 'PyHamcrest', 'jsondiff', 'jsonpath-ng', 'rich'],
)