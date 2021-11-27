from setuptools import setup, find_packages

requirements = [
    'numpy',
    'requests',
    'matplotlib',
    'importlib-metadata',
    'easydict',
    'onnx',
    'sklearn',
    'cython',
    'onnxruntime',
    'opencv-python',
    'tqdm',
    'scikit-image',
    'albumentations',
]

__version__ = 'V0.11.29'

setup(
    # Metadata
    name='meta-face',
    version=__version__,
    author='CachCheng',
    author_email='tkggpdc2007@163.com',
    url='https://github.com/CachCheng/cvface',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    description='Meta Face Toolkit',
    license='Apache-2.0',
    packages=find_packages(exclude=('docs', 'tests', 'scripts')),
    zip_safe=True,
    include_package_data=True,
    install_requires=requirements,
)