from setuptools import setup, find_packages


setup(
    name="dijkstra_alg",
    version="1.0.2",
    description="Пакет для поиска кратчайшего пути посредством алгоритма Дейкстры",
    author="Sokolov Lev",
    author_email="vaxxo9000@gmail.com",
    packages=find_packages(),
    install_requires=['pytest==6.2.5'],
    include_package_data=True,
    package_data={'dijkstra_alg': ['tests/*.txt']}
)