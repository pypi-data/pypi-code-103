import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="freelancing-project-2021",
    version="0.0.2",
    author="Abdallah Ziad",
    author_email="boodyziad1@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={
        'freelancing-project-2021': [
                '*.html',
                '*.css'
                'src/NOWNT/templates/index.html',
                'src/NOWNT/templates/base.html',
                'src/NOWNT/templates/previous.html',
                'src/NOWNT/templates/results.html',
                'src/NOWNT/static/styles/styles.css'
            ]
        },
    include_package_data=True
)
