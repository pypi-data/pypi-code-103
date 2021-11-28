from setuptools import setup, find_packages

setup(name='lab11pkg',
      version='0.1',
      description='Package for lab 11 Python class',
      long_description='Create a package, inside the package, create modules to sort characters and values. Sort modules include - quick sort, bubble sort, merge sort, insertion sort, selection sort, heap sort, radix sort and bucket sort. Finally create a program to execute these sort algorithms on dynamically entered characters and variables.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='Python lab11',
      author='Tatyana Koryakina',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)