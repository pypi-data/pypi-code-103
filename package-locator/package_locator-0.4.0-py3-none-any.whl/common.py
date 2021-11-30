import collections
from urllib.parse import urlparse, parse_qs
import re

CARGO = "Cargo"
COMPOSER = "Composer"
GO = "Go"
MAVEN = "Maven"
NPM = "npm"
NUGET = "NuGet"
PYPI = "pypi"
RUBYGEMS = "RubyGems"
ecosystems = [CARGO, COMPOSER, GO, MAVEN, NPM, NUGET, PYPI, RUBYGEMS]


class NotPackageRepository(Exception):
    pass


class UnknownGitRepositoryDomain(Exception):
    pass


def flatten(dictionary, parent_key=False, separator="."):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    :credit: https://stackoverflow.com/a/6027615/1445015
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flatten({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def get_base_repo_url(repo_url):
    if not isinstance(repo_url, str):
        return None

    parsed_url = urlparse(repo_url)
    host = parsed_url.netloc

    if host == "gitbox.apache.org" and "p" in parse_qs(parsed_url.query).keys():
        project_name = parse_qs(parsed_url.query)["p"]
        return "https://gitbox.apache.org/repos/asf/{}".format(project_name)

    if host == "svn.opensymphony.com":
        return repo_url

    # below rule covers github, gitlab, bitbucket, foocode, eday, qt
    sources = ["github", "gitlab", "bitbucket", "foocode", "eday", "q", "opendev", "foss.heptapod.net"]
    if not any([x in host for x in sources]):
        raise UnknownGitRepositoryDomain
    paths = [s.removesuffix(".git") for s in parsed_url.path.split("/")]
    owner, repo = paths[1], paths[2]
    return "https://{}/{}/{}".format(host, owner, repo)


def search_for_github_repo(data):
    urls = set()
    url_pattern = re.compile(r"""https?:\/\/(?:www\.)?github\.com[^\s)|<|>]+""")
    data = flatten(data)
    for k in data.keys():
        if isinstance(data[k], str) and re.search(url_pattern, data[k]) and " " not in data[k]:
            try:
                urls.add(get_base_repo_url(data[k]))
            except:
                pass

    if not urls:
        for k in data.keys():
            if isinstance(data[k], str):
                candidates = re.findall(url_pattern, data[k])
                for c in candidates:
                    try:
                        urls.add(get_base_repo_url(c))
                    except:
                        pass

    return urls
