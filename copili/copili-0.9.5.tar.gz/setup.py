from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="copili",
    description="Run a series of docker/podman containers, in a coordinated manner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.connect.dzd-ev.de/dzdpythonmodules/copili",
    author="TB",
    author_email="tim.bleimehl@helmholtz-muenchen.de",
    license="MIT",
    packages=["copili"],
    install_requires=["linetimer", "docker", "schedule", "pyyaml", "python-dotenv"],
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
