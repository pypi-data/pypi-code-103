from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

# with open('LICENSE', encoding='utf-8') as f:
#     license = f.read()
#
with open('requirements.txt', encoding='utf-8') as f:
    reqs = f.read()

pkgs = [p for p in find_packages() if p.startswith('zutnlp')]
print(pkgs)
import zutnlp

setup(
    name='zutnlp',
    version=zutnlp.__version__,
    url='https://gitee.com/natural_language_processing/zutnlp',
    description='zutnlp: Deep Learning Toolkit for NLP, developed by zutnlp Team',
    long_description=readme,
    long_description_content_type='text/markdown',
    # license='Apache License',
    author='zutnlp Team',
    author_email="2020107239@zut.edu.cn",
    python_requires='>=3.6',
    packages=pkgs,
    install_requires=reqs.strip().split('\n'),
)
