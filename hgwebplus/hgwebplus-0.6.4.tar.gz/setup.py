from setuptools import setup


setup(
    name='hgwebplus',
    version='0.6.4',
    author='Gary Kramlich',
    author_email='grim@reaperworld.com',
    url='https://keep.imfreedom.org/grim/hgwebplus',
    description='Mercurial plugin to add additional functionality to hgweb',
    packages=['hgext3rd', 'mercurial.templates'],
    package_dir={
        'hgext3rd': 'src',
        'mercurial.templates': 'templates',
    },
    package_data={'mercurial.templates': ['static/*']},
    install_requires=[
        'mistune==2.0.0a4',
        # skip mercurial because it might be installed on the system
        # 'mercurial',
    ],
    license='GPLv2',
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: Software Development :: Version Control',
    ],
)
