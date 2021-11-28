from setuptools import setup, find_packages

GFICLEE_VERSION = '2021.11.28.0.3'

setup(
    name='Cherry_Lolita',
    version=GFICLEE_VERSION,
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    packages=find_packages(),
    include_package_data=True,
    url='https://blog.csdn.net/qq_53280175?spm=1000.2115.3001.5343',
    license='GNU General Public License v3.0',
    author='PYmili',
    author_email='2097632843@qq.com',
    description='Charry 语言gui库',
    classifiers = [
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # 属于什么类型
        'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        'Programming Language :: Python :: 3.9',
    ],
    # 版本限制
    python_requires='>=3.9',
)
