import os
import shutil
import allure


@allure.step('delete dist directory')
def delete_dist_dir(dist_dir):
    if os.path.exists(dist_dir) and os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
    else:
        print("The dist directory does not exist")


@allure.step("build")
def build():
    build_commands = ["python setup.py develop",
                      "python -m pip install --upgrade pip",
                      "python -m pip install --upgrade build", "python -m build", "python setup.py sdist bdist_wheel"]
    for command in build_commands:
        os.system(command)


@allure.step("upload artifact to {azure_feed_name}")
def upload_azure_artifact(azure_feed_name):
    command = f"twine upload -r {azure_feed_name} dist/*"
    os.system(command)


@allure.step("upload pypi artifact")
def upload_pypi_artifact(user, password):
    if user is None:
        command = f"twine upload -u {os.environ.get('pypi-user')} -p {os.environ.get('pypi-password')} --repository-url https://upload.pypi.org/legacy/ dist/*"
    else:
        command = f"twine upload -u {user} -p {password} --repository-url https://upload.pypi.org/legacy/ dist/*"

    os.system(command)


@allure.feature('Build & Upload New Artifact To Azure')  # A sub-function function at large
def run_process(dist_dir, azure_feeds: list = None, azure_artifact: bool = False, pypi_artifact: bool = False,
                user=None, password=None):
    delete_dist_dir(dist_dir)
    build()
    if pypi_artifact:
        upload_pypi_artifact(user=user, password=password)

    if azure_artifact:
        for feed in azure_feeds:
            upload_azure_artifact(feed)
