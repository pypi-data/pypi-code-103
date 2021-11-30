from setuptools import setup

setup(
    name="DZDutils",
    description="Tool collection from the DZD Devs",
    url="",
    author="TB",
    author_email="tim.bleimehl@helmholtz-muenchen.de",
    license="MIT",
    packages=["DZDutils", "DZDutils.inspect"],
    install_requires=["py2neo", "numpy", "linetimer", "graphio"],
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        # "local_scheme": "node-and-timestamp"
        "local_scheme": "no-local-version",
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
