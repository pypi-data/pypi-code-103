import re

from flask import Blueprint, abort, current_app, render_template, redirect

class NormalizePackageName:
    re_normalize = re.compile(r'[-_\.]+')

    @classmethod
    def normalize(cls, package_name):
        return cls.re_normalize.sub("-", package_name).lower()

blueprint = Blueprint('package_file_list', __name__)

@blueprint.route('/<string:package_name>')
def PackageFileListRedirect(package_name):
    return redirect(f'/{package_name}/', code=302)

@blueprint.route('/<string:package_name>/')
def PackageFileList(package_name):
    if len(package_name) > 1024:
        abort(400, "Package names must be less than 1024 characters in length")

    if not package_name.isascii():
        abort(400, "Package name must be made up of only ascii characters")

    normalized_package_name = NormalizePackageName.normalize(package_name)
    if normalized_package_name != package_name:
        return redirect(f'/{normalized_package_name}', code=302)

    results = None
    for repo in current_app.repositories:
        list_result = repo.list_package_files(package_name)
        if list_result.ok:
            results = list_result.get_results()
            break

    if results is None:
        abort(404, "Package not found")

    return render_template("package_file_list.html", list_results=results, package_name=package_name)

@blueprint.route('')
def PackageListRedirect():
    return redirect(f'', code=302)

@blueprint.route('/')
def PackageList():
    all_packages = set()
    for repo in current_app.repositories:
        current_app.logger.debug(f"Requesting list of packages from {repo.baseurl}")
        list_result = repo.list_packages()
        current_app.logger.debug("Updating package list")
        if list_result.ok:
            all_packages.update([pkg.name for pkg in list_result.get_results()])
    current_app.logger.debug("Collected package list")

    return render_template("package_list.html", list_results=list(sorted(all_packages)))
