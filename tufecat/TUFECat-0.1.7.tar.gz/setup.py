# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages
 
setup(name = 'TUFECat',     # 包名
      version = '0.1.7',  # 版本号
      description = 'A data kit for financial students.',
      long_description = 'Built by Dai Mingwei and his team. For student from TUFE and other colleges.\
          This version is still a test development version, which can be used for TextAnalysisCat, a kitten that can now complete the work when text sentimental tendency is scored with word cloud drawing. At the end of July, another kitten named TimeSeriseCat will be developed.\
              TimeSeriseCat will build on The Prophet, a time series prediction algorithm developed by Facebook, to provide a simpler, easier-to-operate function interface.\
                  When TimeSeriseCat is developed, TUFECat will enter the 0.1.0 phase. At 0. Each update in the X.X phase means that a new kitten has been developed or that individual kittens have learned new skills.\n\
                      Version 0.1.0 is a big update, and the TUFECat family has added a new kitten that will address your needs for time series data analysis.At present, the kitten can provide time series prediction, time series component display and prediction results output three functions, and the implementation of all three functions only need a line of code.\
                \n\n\
                    In version 0.1.5, TimeSeriseCat implemented the ARIMA model, which includes ARIMA_Prefare and ARIMA_Model functions. The former can achieve the stability test and data split of time series, and give the relevant visual images. The latter can use the ARIMA model to make timing predictions with a given parameter.\
                      \n\n\ In version 0.1.7, we have added the LDA model and keyword extraction functions, which are in TextAnalysisCat.  ', 
      author = 'Dai Mingwei',
      author_email = 'daimingwei@tcsx1000.onexmail.com',
      url = '',
      license = '',
      install_requires = ['wordcloud>=1.8.1',
                          'jieba>=0.42.1',
                          'matplotlib>=3.3.2',
                          'pandas>=1.1.3',
                          'fbprophet>=0.7.1',
                          'numpy>=1.19.2',
                          'plotly>=4.14.3',
                          'plotly-express>=0.4.1',
                          'statsmodels>=0.12.0',
                          'snownlp>=0.12.3',
                          'nltk>=3.5',
                          'stop_words>=2018.7.23',
                          'gensim>=4.1.2'],
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
      ],
      keywords = '',
      packages = find_packages('src'),  # 必填，就是包的代码主目录
      package_dir = {'':'src'},         # 必填
      include_package_data = True,
)

