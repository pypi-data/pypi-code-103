from setuptools import setup, find_packages

# INSTALL_PACKAGES = open(path.join(DIR, 'requirements.txt')).read().splitlines()

setup(
    name='mysqlx',
    packages=find_packages(),
    description="mysqlx is a simple python sql executor for MySQL like iBatis.",
    long_description_content_type='text/markdown',
    install_requires=[
        'Jinja2>=3.0.3',
        'mysql-connector-python>=8.0.27',
    ],
    version='1.0.1',
    url='https://github.com/nzhzds/mysqlx/mysqlx',
    author='summry',
    author_email='xiazhongbiao@126.com',
    keywords=['sql', 'MySQL', 'iBatis', 'MyBatis', 'python'],
    package_data={
        # include json and txt files
        '': ['*.rst', '*.txt'],
    },
    include_package_data=True,
    python_requires='>=3.6.0',
    zip_safe=False
)

