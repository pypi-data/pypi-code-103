from os import getenv
from time import sleep
from octohot.cli.config import config
from github3 import GitHub


rate_limit = int(getenv('GITHUB_RATE_LIMIT', "500"))
timeout = int(getenv('GITHUB_TIMEOUT', "10"))


def get_token():
    try:
        token = config['github_token']
    except Exception as e:
        print(e)
        print('\nTrying to use GITHUB_TOKEN environment variable')
        token = getenv('GITHUB_TOKEN', '')

    if not token:
        raise Exception("Missing token")

    return token


def login():
    token = get_token()
    git = GitHub()
    git.login(token=token)
    return git


def is_archived(_repository):
    git = login()
    repo = git.repository(_repository.owner, _repository.name)
    return repo.archived


def check_rate_limit(_client):
    while True:
        remaining = _client.ratelimit_remaining
        if remaining < 500:
            print(f'\n>>>>>> Your rate limit is set to {rate_limit} and you only have {remaining}.')
            print(f'>>>>>> Trying again in {timeout} seconds...\n')
            sleep(timeout)
            continue
        break

