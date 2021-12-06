import setuptools

long_desc = open("README.md").read()
required = [
    'torch',
    'tqdm', 'pyyaml', 'numpy', 'matplotlib',
    'scikit-image', 'scikit-learn', 'opencv-python',
    'timm', 'xmltodict', 'tensorboard']

setuptools.setup(
    name="py-blueprint",
    version="0.0.1-1",
    author="Hao Yang",
    author_email="yanghao.alexis@foxmail.com",
    license="MIT",
    description="Configure Python to Yaml.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/YANG-H/BluePrint.git",
    packages=['blueprint', 'blueprint.ml', 'blueprint.ml.augmenters',
              'blueprint.ml.datasets'],
    key_words="Configuration, machine learning",
    install_requires=required,
    python_requires=">=3.7",
)
