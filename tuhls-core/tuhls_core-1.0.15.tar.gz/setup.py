from setuptools import find_packages, setup

import versioneer

setup(
    name="tuhls_core",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    package_data={
        "tuhls_design": ("static/country_flags/svg/*.svg", "static/css/dist/style.css"),
        "tuhls_invoice": ("data/*.svg", "templates/**/*.html"),
        "tuhls_request_logger": ("templates/**/*.html",),
    },
    install_requires=["django"],
    license_files=("LICENSE",),
    url="https://gitlab.com/tuhls/tuhls_core",
    author="Herbert Rusznak (tlb)",
    author_email="herbert.rusznak@gmail.com",
    license="MIT",
    python_requires=">=3.8",
)
