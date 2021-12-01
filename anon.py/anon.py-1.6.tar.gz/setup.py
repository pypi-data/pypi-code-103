from setuptools import setup, find_packages

requirements = [
    "aiohttp", 
    "ujson"
]

setup(name = "anon.py",
      version = "1.6",
      description = "A library for interacting with the API of the Anonym application, because of which the server takes you for a regular user of the application",
      packages = ["anonym", "anonym.util"],
      author_email = "ktoya170214@gmail.com",
      install_requires = requirements,
      zip_safe = False)