import tempfile
import os
import json
from git import Repo
from pathlib import Path
from os.path import join, relpath, isfile
import toml
import re
import requests
from zipfile import ZipFile
import tarfile

from package_locator.common import NotPackageRepository


class UncertainSubdir(Exception):
    pass


def locate_file_in_dir(path, target_file):
    """locate *filepath"""
    candidates = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = join(root, file)
            if filepath.endswith(target_file):
                candidates.append(relpath(filepath, path))
    return candidates


def locate_dir_in_repo(repo_path, target_dir):
    """return the top-level dir"""
    candidates = []
    for root, dirs, files in os.walk(repo_path):
        for dir in dirs:
            if dir.endswith(target_dir):
                candidates.append(relpath(join(root, dir), repo_path))
    return candidates


def get_package_name_from_npm_json(filepath):
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return data.get("name", None)
        except:
            # there could be test files for erroneous data
            return None


def get_package_name_from_composer_json(filepath):
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return data.get("name", None)
        except:
            # there could be test files for erroneous data
            return None


def get_package_name_from_cargo_toml(filepath):
    with open(filepath, "r") as f:
        try:
            data = toml.load(f)
            return data.get("package", {}).get("name", None)
        except:
            # there could be test files for erroneous data
            return None


def get_npm_subdir(package, repo_url):
    manifest_filename = "package.json"
    temp_dir = tempfile.TemporaryDirectory()
    repo = Repo.clone_from(repo_url, temp_dir.name)
    repo_path = Path(repo.git_dir).parent

    subdirs = locate_file_in_dir(repo_path, manifest_filename)
    for subdir in subdirs:
        name = get_package_name_from_npm_json(join(repo_path, subdir))
        if name and (name.endswith(package) or name.replace("/", "-").endswith(package.replace("/", "-"))):
            return subdir.removesuffix(manifest_filename)
    raise NotPackageRepository


def get_rubygems_subdir(package, repo_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_filename = ".gemspec".format(package)
        repo = Repo.clone_from(repo_url, temp_dir)
        repo_path = Path(repo.git_dir).parent

        candidate_manifests = locate_file_in_dir(repo_path, manifest_filename)
        for candidate in candidate_manifests:
            # first check the gemspec name
            if candidate.split("/")[-1] == "{}.gemspec".format(package):
                return str(Path(candidate).parent)
            else:
                # check gem name within the file
                pattern = re.compile(r"""name(\s*)=(\s*)("|'){}("|')""".format(package))
                with open(join(repo_path, candidate), "r") as f:
                    if any([re.search(pattern, line) for line in f]):
                        return str(Path(candidate).parent)

        # match top-level ruby files
        with tempfile.TemporaryDirectory() as temp_dir_b:
            url = get_rubygem_download_url(package)
            path = download_ruby_gem(url, temp_dir_b)
            # a heuristic based on lib
            if "lib" in os.listdir(path):
                path = join(path, "lib")
                libfiles = [f for f in os.listdir(path) if f.endswith(".rb")]
                for root, dirs, files in os.walk(repo_path):
                    for dir in dirs:
                        if dir == "lib":
                            if all([f in os.listdir(join(root, dir)) for f in libfiles]):
                                return relpath(root, repo_path)
        raise UncertainSubdir


def get_composer_subdir(package, repo_url):
    manifest_filename = "composer.json"
    temp_dir = tempfile.TemporaryDirectory()
    repo = Repo.clone_from(repo_url, temp_dir.name)
    repo_path = Path(repo.git_dir).parent

    subdirs = locate_file_in_dir(repo_path, manifest_filename)
    for subdir in subdirs:
        if get_package_name_from_composer_json(join(repo_path, subdir)) == package:
            return subdir.removesuffix(manifest_filename)
    raise NotPackageRepository


def get_cargo_subdir(package, repo_url):
    manifest_filename = "Cargo.toml"
    temp_dir = tempfile.TemporaryDirectory()
    repo = Repo.clone_from(repo_url, temp_dir.name)
    repo_path = Path(repo.git_dir).parent

    subdirs = locate_file_in_dir(repo_path, manifest_filename)
    for subdir in subdirs:
        if get_package_name_from_cargo_toml(join(repo_path, subdir)) == package:
            return subdir.removesuffix(manifest_filename)
    raise NotPackageRepository


def download_ruby_gem(url, path):
    dest_file = "gem.tar.gz"
    dest_file = "{}/{}".format(path, dest_file)
    r = requests.get(url, stream=True)
    with open(dest_file, "wb") as output_file:
        output_file.write(r.content)
        # extract file
    t = tarfile.open(dest_file)
    t.extractall(path)

    # extract again
    dest_file = "data.tar.gz"
    dest_file = join(path, dest_file)
    t = tarfile.open(dest_file)
    t.extractall(path)

    t.close()
    return path


def get_rubygem_download_url(package):
    url = "https://rubygems.org/api/v1/gems/{}.json".format(package)
    page = requests.get(url)
    data = json.loads(page.content)
    version = data["version"]
    return "https://rubygems.org/downloads/{}-{}.gem".format(package, version)


def get_pypi_download_url(package):
    # get download link for the latest wheel
    url = "https://pypi.org/pypi/{}/json".format(package)
    page = requests.get(url)
    data = json.loads(page.content)["releases"]
    data = {k: v for k, v in data.items() if v}
    ## get latest release
    data = sorted(data.items(), key=lambda item: item[1][-1]["upload_time"])
    if data:
        data = data[-1][1]
        ## search for wheel distribution
        url = next((x["url"] for x in data if x["url"].endswith(".whl")), data[-1]["url"])
        return url


def download_pypi_package(url, path):
    if url.endswith(".tar.gz"):
        dest_file = "wheel.tar.gz"
        dest_file = "{}/{}".format(path, dest_file)
        r = requests.get(url, stream=True)
        with open(dest_file, "wb") as output_file:
            output_file.write(r.content)
        # extract file
        t = tarfile.open(dest_file)
        t.extractall(path)
        t.close()
    else:
        dest_file = "wheel.zip"
        dest_file = "{}/{}".format(path, dest_file)
        r = requests.get(url, stream=True)
        with open(dest_file, "wb") as output_file:
            output_file.write(r.content)
        z = ZipFile(dest_file, "r")
        z.extractall(path)
        z.close()

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith("-info"):
                return root

        for file in files:
            if file.endswith("setup.py"):
                return root
    return path


def get_pypi_init_file(path):
    init_files = locate_file_in_dir(path, "__init__.py")
    if init_files:
        # we want to ge the the top-level init file
        init_files.sort(key=lambda x: len(x.split("/")))
        return init_files[0]
    else:
        return None


def get_pypi_subdir(package, repo_url):
    """
    There is no manifest file for pypi
    We work on the heuristic that python packages have a common pattern
    of putting library specific code into a directory named on the package
    and then checking if the directory contains a __init__.py files
    indicating to be a python module
    """
    with tempfile.TemporaryDirectory() as temp_dir_a, tempfile.TemporaryDirectory() as temp_dir_b:
        repo = Repo.clone_from(repo_url, temp_dir_a)
        repo_path = Path(repo.git_dir).parent

        url = get_pypi_download_url(package)
        path = download_pypi_package(url, temp_dir_b)

        init_file = get_pypi_init_file(path)
        if init_file:
            dirs = locate_file_in_dir(repo_path, init_file)

            if not dirs:
                # do reverse matching
                candidates = locate_file_in_dir(repo_path, "__init__.py")
                candidates = [c for c in candidates if init_file.endswith(c)]
                if len(candidates) == 1:
                    subdir = ""
                else:
                    raise NotPackageRepository

            elif len(dirs) == 1:
                subdir = dirs[0]

            else:
                if init_file in dirs:
                    subdir = init_file
                else:
                    # heuristic: package name in
                    dirs = [d for d in dirs if package in d.split("/")]
                    if len(dirs) == 1:
                        subdir = dirs[0]
                    else:
                        raise UncertainSubdir

            return subdir.removesuffix(init_file)

        else:
            # get top level py files
            pyfiles = [f for f in os.listdir(path) if isfile(join(path, f)) and f.endswith(".py")]
            candidates = {}
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file in pyfiles:
                        candidates[root] = candidates.get(root, 0) + 1
            for k in candidates.keys():
                if candidates[k] == len(pyfiles):
                    return relpath(k, repo_path)

            raise UncertainSubdir
