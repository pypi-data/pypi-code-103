from setuptools import setup, find_packages
"""
打包的用的setup必须引入，
"""

VERSION = '0.1.1'

setup(name='mtpdocr',
      version=VERSION,
      description="OCR",
      long_description='just enjoy',
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python OCR base on paddleOCR',
      author='allen',
      author_email='310315734@qq.com',
      url='https://github.com/AllenCall/paddleOCRDemo',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      dependency_links=["https://mirror.baidu.com/pypi/simple", "https://test.pypi.org/simple/"],
      install_requires=[
        'paddleocr == 2.2',
        'paddlepaddle',
      ],
      entry_points={
        'console_scripts':[
            'mtpdocr = OCR.getCor:getCor'
        ]
      },
)