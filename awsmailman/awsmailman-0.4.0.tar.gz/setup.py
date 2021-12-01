import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='awsmailman',
    packages=['awsmailman'],
    version='0.4.0',
    license='MIT',
    description='A utility for updating domain registrant information in Amazon Route 53',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Fernando Medina Corey',
    author_email='fernandomc.sea@gmail.com',
    url='https://github.com/fernando-mc/aws-mailman',
    keywords=['AWS', 'Route53', 'Domains'],
    entry_points={
        'console_scripts': [
            'awsmailman=awsmailman.mailman:main',
        ],
    },
    install_requires=[
        'boto3',
        'bullet',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
  ],
)