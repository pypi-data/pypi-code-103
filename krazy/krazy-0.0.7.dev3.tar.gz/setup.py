# from setuptools import setup

# setup(name='krazy',
# version='0.5',
# description="Karik's own package. In this version, added payment ocr for gpay and paytm. Gpay Bug in PaymentOCR fixed.",
# url='#',
# author='Kartik',
# author_email='kartik@live.com',
# license='None',
# packages=['krazy'],
# zip_safe=False)

# X.YaN   # Alpha release
# X.YbN   # Beta release
# X.YrcN  # Release Candidate
# X.Y     # Final release

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="krazy",
    version="0.0.7.dev3",
    author="Kartik",
    author_email="kartik@live.com",
    description="My own small package of uitilities I use.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kartikjain11/krazy",
    project_urls={
        "Bug Tracker": "https://github.com/kartikjain11/krazy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "krazy"},
    packages=setuptools.find_packages(where="krazy"),
    python_requires=">=3.8.11",
    install_requires=['pandas','openpyxl','gspread','oauth2client','pytesseract','pytz','time'],
)