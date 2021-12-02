from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
        name="simple_calculator_test", 
        version='1.0',
        author="Author",
        author_email="email@gmail.com",
        description='Caculator for addition and subtraction',
        long_description=long_description,
        long_description_content_type="text/markdown",
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ],
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        python_requires=">=3.5",
)

