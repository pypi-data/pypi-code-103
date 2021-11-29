from pdx import Session
from pdx import Console
from pdx import utility_service
from pdx import Executor
import json
import requests

api_url_base = 'https://git.oit.pdx.edu/rest/api/1.0/'


def bb_url(given_url):
    """Used to turn a partial URL into a full URL (so functions can accept either)"""
    if given_url.startswith('https'):
        # Use the given URL, but strip double-slash if resulted from concatenating the base with the suffix
        return given_url.replace('1.0//', '1.0/').strip()
    else:
        # Add the base URL, and strip double-slash if resulted from concatenating the base with the suffix
        return f"{api_url_base}{given_url}".replace('1.0//', '1.0/').strip()


def curl_userpass_string():
    return "{0}:{1}".format(Session.username, utility_service.get_odin_pw())


def api_get(url):
    exe = Executor.Executor(['curl', '-u', curl_userpass_string(), bb_url(url)])
    json_response = exe.get_output()
    response_data = json.loads(json_response)
    # review_response(response_data)
    return response_data


def api_post(url, payload=None):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'xx',
        "Origin": "https://git.oit.pdx.edu/",
        "X-Atlassian-Token": "nocheck"
    }
    response = requests.post(
        bb_url(url),
        auth=(Session.username, utility_service.get_odin_pw()),
        data=payload,
        headers=headers
    )
    review_response(response)
    json_response = response.text
    response_data = json.loads(json_response)

    return response_data


def review_response(response):
    out = Console.get()
    # If status code indicates success
    if response.status_code < 300:
        return True

    else:
        error_printed = False

        # Print any error messages detected in the response
        response_data = json.loads(response.text)
        if 'errors' in response_data and type(response_data['errors']) is list:
            for error_data in response_data['errors']:
                if 'message' in error_data:
                    out.put_error(error_data['message'])
                    error_printed = True

        # If not errors were printed, print an error about the status code
        if not error_printed:
            out.put_error(f"{response.url} returned status code: {response.status_code}")

        return False


# Call API to create a pull request
def pull_request(
        project,
        repo,
        from_branch,
        to_branch,
        approver,
        title,
        description
):
    out = Console.get()
    try:
        body = """{openBracket}
            "title": "{title}",
            "description": "{description}",
            "state": "OPEN",
            "open": true,
            "closed": false,
            "fromRef": {openBracket}
                "id": "refs/heads/{from_branch}",
                "repository": {openBracket}
                    "slug": "{repo}",
                    "name": null,
                    "project": {openBracket}
                        "key": "{project}"
                    {closeBracket}
                {closeBracket}
            {closeBracket},
            "toRef": {openBracket}
                "id": "refs/heads/{to_branch}",
                "repository": {openBracket}
                    "slug": "{repo}",
                    "name": null,
                    "project": {openBracket}
                        "key": "{project}"
                    {closeBracket}
                {closeBracket}
            {closeBracket},
            "locked": false,
            "reviewers": [
                {openBracket}
                    "user": {openBracket}
                        "name": "{approver}"
                    {closeBracket}
                {closeBracket}
            ]
        {closeBracket}""".format(
            openBracket='{',
            closeBracket='}',
            title=title,
            description=description,
            from_branch=from_branch,
            to_branch=to_branch,
            repo=repo,
            project=project,
            approver=approver
        )

        url = api_url_base + f"projects/{project}/repos/{repo}/pull-requests"
        api_post(url, payload=body)

    except Exception as ee:
        out.unexpected_error(ee, 'error creating pull request')
