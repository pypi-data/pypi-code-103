import setuptools

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="cesloi",
    version="0.6.2",
    author="ArcletProject",
    author_email="rf_tar_railt@qq.com",
    description="An simple Python SDK base on mirai-api-http v2",
    license='AGPL 3.0',
    long_description=long_description,
    long_description_content_type="text/rst",
    url="https://github.com/RF-Tar-Railt/Cesloi",
    install_requires=['aiohttp', 'yarl', 'pydantic', 'loguru', 'arclet-letoderea'],
    packages=['arclet.cesloi', 'arclet.cesloi.event', 'arclet.cesloi.message', 'arclet.cesloi.model', 'arclet.cesloi.timing'],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords='mirai, bot, asyncio, http, websocket',
    python_requires='>=3.8'
)
