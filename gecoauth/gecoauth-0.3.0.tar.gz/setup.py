import setuptools

VERSION         = "0.3.0"
PACKAGE_NAME    = "gecoauth"
AUTHOR          = "Lorenzo Borelli"
EMAIL           = "lorenzo.borelli@gecosistema.com"
GITHUB          = "https://github.com/Plutone11011/geco_auth.git"
DESCRIPTION     = "A Django app that extends django-rest-auth."

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    url=GITHUB,
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=(
        "Environment :: Web Environment",
        "Framework :: Django",
        #Framework :: Django :: 3.2 # Replace "X.Y" as appropriate
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ),
    install_requires=[
        "Django",  # Replace "X.Y" as appropriate
        "djangorestframework", 
        "django-rest-auth", 
        "django-allauth"
    ]
)