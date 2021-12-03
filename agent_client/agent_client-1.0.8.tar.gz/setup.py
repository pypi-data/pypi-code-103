from setuptools import setup, find_packages
#python setup.py sdist upload  
setup(
    name = 'agent_client',
    version = '1.0.8',
    keywords = ['runner', 'client'],
    description = 'REST Runner',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
      ],
    license = 'MIT License',
	url = 'https://pypi.org/project/agent_client',
    install_requires = ['simplejson>=1.1',
						'PyMySQL',
						'DBUtils',
						'flask',
						'flask-restful'],
    author = 'yuwen123441',
    author_email = 'yuwen123441@126.com',
    packages = find_packages(),
    include_package_data=True, 
    platforms = 'any',
)