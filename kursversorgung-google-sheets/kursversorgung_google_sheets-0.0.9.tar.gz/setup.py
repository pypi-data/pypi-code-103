from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent


VERSION = '0.0.9'
DESCRIPTION = 'Kursversorgung Google Sheets'
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="kursversorgung_google_sheets",
    version=VERSION,
    author="Valentin Baier",
    author_email="valentin_baier@gmx.de",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['exchangelib', 'setuptools', 'gspread', 'pandas', 'oauth2client', 'pretty_html_table',
                      'google-api-python-client', 'bs4', 'beautifulsoup4', 'blpapi', 'xbbg', 'future', 'tzdata'],
    keywords=['python', 'kursversorgung', 'warrants', 'updateLast', 'updateSecurityName', 'updateLastSplits'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
