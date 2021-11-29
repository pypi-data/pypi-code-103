import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="npd-category-correlation",
    version="0.0.2",
    author="Max Leonard",
    author_email="maxhleonard@gmail.com",
    description="Library for calculating NPD Category Correlations with Financial Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://NPDGroup@dev.azure.com/NPDGroup/NPDFinancialServices/_git/NPDCategoryCorrelation",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src","npd_cat_corr":"src/npd_cat_corr"},
    packages=["npd_cat_corr"],
    python_requires=">=3.6",
    install_requires = [
        "pandas",
        "blapi"
    ]
)