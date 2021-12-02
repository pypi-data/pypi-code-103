import setuptools

# with open('../README.md') as fp1, open('README.md') as fp2:
#     long_description = fp1.read() + '\n\n' + fp2.read() # TODO: maybe revise?


setuptools.setup(
    name = 'iterjson',
    version = '1.0.0b1',
    url = 'https://github.com/Gaming32/iterjson',
    project_urls = {
        'Source': 'https://github.com/Gaming32/iterjson/tree/main/py',
        'Tracker': 'https://github.com/Gaming32/iterjson/issues',
    },
    author = 'Gaming32',
    author_email = 'gaming32i64@gmail.com',
    license = 'License :: OSI Approved :: MIT License',
    description = 'Library for parsing JSON without loading the whole document into memory',
    # long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = [
        'iterjson'
    ],
)
