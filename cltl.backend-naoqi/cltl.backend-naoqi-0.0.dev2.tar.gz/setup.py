from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name='cltl.backend-naoqi',
    version=version,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    data_files=[('VERSION', ['VERSION'])],
    url="https://github.com/leolani/cltl-backend-naoqi",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Backend for Pepper robot',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=2.7.10',
    install_requires=["numpy==1.16.2",
                      "flask==0.12.5",
                      "click==7.0",
                      "enum34==1.1.10"]
)
