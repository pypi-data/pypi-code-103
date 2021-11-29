from setuptools import setup

readme = open("./README.md","r")

setup(
    name = "ForYou",
    version = "0.1",
    description="Es un paquete para alguin especial",
    long_description=readme.read(),
    long_description_content_type='text/markdown',
    author="Caros Garcia Garcia",
    author_email = "tigrecarlos1@gmail.com",
    # REPOSITORIO GIT
    url = "https://github.com/CarlosGr10/ForYou.git",
    download_url='https://github.com/CarlosGr10/ForYou.git/tarball/01',
    kwargs = ['love','crush','ForYou'],
    license='MIT',
    packages=["Modulo_love"],
    include_package_data=True
    )
