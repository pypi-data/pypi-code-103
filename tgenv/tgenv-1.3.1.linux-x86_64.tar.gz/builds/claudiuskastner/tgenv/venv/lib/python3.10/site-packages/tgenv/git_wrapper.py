"""    This file is part of tgenv.

    tgenv is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    tgenv is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with tgenv.  If not, see <https://www.gnu.org/licenses/>.
"""

from github import Github

from .asset_downloader import download_asset

def get_versions(repository, git_token=""):
    """ Gets all published version of a repo
    """
    if git_token:
        github = Github(git_token)
    else:
        github = Github()
    repo = github.get_repo(repository)
    releases = repo.get_releases()
    release_names = []
    for release in releases:
        release_names.append(release.tag_name)
    return release_names

def get_release_asset(repository: str, release_name: str, versions_path: str,git_token=""):
    """ Downloads the specified release asset
    """

    if git_token:
        github = Github(git_token)
    else:
        github = Github()
    repo = github.get_repo(repository)
    release = repo.get_release(release_name)
    assets = release.get_assets()
    for asset in assets:
        if asset.name == "terragrunt_linux_amd64":
            linux_amd64_asset = asset
            break
    url = linux_amd64_asset.browser_download_url
    download_asset(url, versions_path + release_name, git_token)
