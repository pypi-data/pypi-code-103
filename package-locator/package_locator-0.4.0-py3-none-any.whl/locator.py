from os import cpu_count
from re import sub

from git import exc
from package_locator.common import *
from package_locator.directory import *
import requests
import json


def get_npm_location(package):
    url = "https://registry.npmjs.org/{}".format(package)
    data = json.loads(requests.get(url).content)

    # TODO: do all npm packages have repo_url data?
    repo_url = get_base_repo_url(data["repository"]["url"])
    directory = data["repository"].get("directory", None)
    if directory:
        return repo_url, directory
    try:
        subdir = get_npm_subdir(package, repo_url)
        return repo_url, subdir
    except Exception as e:
        print(e)
        return repo_url, None


def get_rubygems_location(package):
    url = "https://rubygems.org/api/v1/gems/{}.json".format(package)
    data = json.loads(requests.get(url).content)
    repo_url = get_base_repo_url(data.get("source_code_uri", None))
    if repo_url:
        try:
            subdir = get_rubygems_subdir(package, repo_url)
            return repo_url, subdir
        except Exception as e:
            print(e)
            return repo_url, None

    urls = search_for_github_repo(data)
    for url in urls:
        try:
            url = get_base_repo_url(url)
            subdir = get_rubygems_subdir(package, url)
            return url, subdir
        except Exception as e:
            print(e)
            continue
    return None, None


def get_pypi_location(package):
    url = "https://pypi.org/pypi/{}/json".format(package)
    data = json.loads(requests.get(url).content)
    try:
        repo_url = get_base_repo_url(data["info"]["project_urls"]["Source Code"])
    except:
        repo_url = None

    if repo_url:
        try:
            subdir = get_pypi_subdir(package, repo_url)
            return repo_url, subdir
        except:
            return repo_url, None

    urls = search_for_github_repo(data)
    for url in urls:
        try:
            url = get_base_repo_url(url)
            subdir = get_pypi_subdir(package, url)
            return url, subdir
        except:
            continue

    try:
        homepage = data["info"]["home_page"]
    except:
        homepage = None
    if homepage:
        homepage = {"body": requests.get(homepage).text}
        urls = search_for_github_repo(homepage)
        for url in urls:
            try:
                url = get_base_repo_url(url)
                subdir = get_pypi_subdir(package, url)
                return url, subdir
            except:
                continue

    return None, None


def get_composer_location(package):
    url = "https://repo.packagist.org/p2/{}.json".format(package)
    data = json.loads(requests.get(url).content)
    data = data["packages"][package][0]
    try:
        repo_url = get_base_repo_url(data["source"]["url"])
    except:
        repo_url = None

    if repo_url:
        try:
            subdir = get_composer_subdir(package, repo_url)
            return repo_url, subdir
        except:
            return repo_url, None

    urls = search_for_github_repo(data)
    for url in urls:
        try:
            url = get_base_repo_url(url)
            subdir = get_composer_subdir(package, url)
            return url, subdir
        except:
            continue
    return None, None


def get_cargo_location(package):
    url = "https://crates.io/api/v1/crates/{}".format(package)
    data = json.loads(requests.get(url).content)["crate"]
    repo_url = get_base_repo_url(data.get("repository", None))
    if repo_url:
        try:
            subdir = get_cargo_subdir(package, repo_url)
            return repo_url, subdir
        except:
            return repo_url, None

    urls = search_for_github_repo(data)
    for url in urls:
        try:
            url = get_base_repo_url(url)
            subdir = get_cargo_subdir(package, url)
            return url, subdir
        except:
            continue
    return None, None


def get_repository_url_and_subdir(ecosystem, package):
    if ecosystem == NPM:
        repo_url, subdir = get_npm_location(package)
    elif ecosystem == PYPI:
        repo_url, subdir = get_pypi_location(package)
    elif ecosystem == RUBYGEMS:
        repo_url, subdir = get_rubygems_location(package)
    elif ecosystem == COMPOSER:
        repo_url, subdir = get_composer_location(package)
    elif ecosystem == CARGO:
        repo_url, subdir = get_cargo_location(package)

    if repo_url and subdir is not None:
        subdir = subdir.removesuffix("/").removesuffix(".")
        if not subdir.startswith("./"):
            subdir = "./" + subdir
        repo_url = get_base_repo_url(repo_url)

    return repo_url, subdir
