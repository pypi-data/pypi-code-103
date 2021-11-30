import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="django_mazer",
	version="0.0.12",
	author="Nikita Marchenko",
	author_email="megaelebrus@gmail.com",
	description="Django Template Mazer",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/ElebrUS/DjangoMazer",
	packages=['mazer', 'mazer.templatetags'],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
