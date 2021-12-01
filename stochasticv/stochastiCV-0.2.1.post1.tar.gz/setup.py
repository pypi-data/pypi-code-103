from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='stochastiCV',
    version='0.2.1.post1',
    packages=['stochastiCV'],
    description='A method of cross-validation based on scikit-learn that splits data into subsampling or k-folds splits (using random or assigned seed values) and then repeats the model multiple times using different seeds. This function enables a more statistical and scientific method of investigating model performance.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mjkleiman/stochastiCV",
    project_urls={
        "Issue Tracker": "https://github.com/mjkleiman/stochastiCV/issues"
    },
    author='Michael J Kleiman',
    author_email='michael@kleiman.me',
    license='BSD-3',
    include_package_data=True
)
