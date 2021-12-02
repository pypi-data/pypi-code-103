import io

from setuptools import find_namespace_packages, setup

import os

__name__ = 'vatis_asr_client'
__tag__ = '1.2.0'
__short_description__ = 'Python implementation of the client for Vatis\'s ASR services'
__download_url__ = 'https://gitlab.com/vatistech/asr-client-python/-/archive/{__tag__}/asr-client-python-{__tag__}.zip'\
    .format(__tag__=__tag__)

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
__release_status__ = "Development Status :: 4 - Beta"


def req_file(filename, folder="requirements"):
    with open(os.path.join(folder, filename)) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters
    # Example: `\n` at the end of each line
    return [x.strip() for x in content]


install_requires = req_file('requirements.txt')
extras_require = {
    'remote': req_file('requirements_remote.txt'),
    'standalone': req_file('requirements_standalone.txt')
}

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.md")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

packages = find_namespace_packages(include=['vatis.*'])

namespaces = ['vatis']

setup(
    name=__name__,
    version=__tag__,
    description=__short_description__,
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://gitlab.com/vatistech/asr-client-python',
    download_url=__download_url__,
    maintainer='VATIS TECH',
    maintainer_email='founders@vatis.tech',
    packages=packages,
    namespace_packages=namespaces,
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    zip_safe=False,
    python_requires=">=3.6",
    platforms="Posix; MacOS X; Windows",
    license='Apache Software License',
    classifiers=[
        __release_status__,
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Internet"
    ]
)
