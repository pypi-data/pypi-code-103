from os import getenv
from jira import JIRA
from .logger import get_logger
from jira.exceptions import JIRAError


def _get_client(api_server=None, api_user=None, api_key=None):
    logger = get_logger(__name__)
    api_user = getenv("JIRA_API_USER", api_user)
    api_key = getenv("JIRA_API_KEY", api_key)
    if not api_user:
        logger.error(
            "api_user argument is not provided and JIRA_API_USER is not present in the environment"
        )
        return None
    if not api_key:
        logger.error(
            "api_key argument is not provided and JIRA_API_KEY is not present in the environment"
        )
        return None
    return JIRA(server=api_server, basic_auth=(api_user, api_key))


def get_jira_issue(
    id,
    fields=None,
    expand=None,
    api_server="https://jira.atlassian.com",
    api_user=None,
    api_key=None,
):
    """Get an issue Resource from the jira server

    :param id: ID or key of the issue to get
    :type id: Union[Issue, str]
    :param fields: comma-separated string of issue fields to include in the results
    :type fields: Optional[str]
    :param expand: extra information to fetch inside each resource
    :type expand: Optional[str]
    :param api_server: jira api server url(default: https://jira.atlassian.com)
    :type api_server: str
    :param api_user: jira api user. If api_user is none, JIRA_API_USER environment value will be assigned.
    :type api_user: str
    :param api_key: jira user api key. If api_key is none, JIRA_API_KEY environment value will be assigned.
    :type api_key: str
    :return: `jira.Issue` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    jira = _get_client(api_server=api_server, api_user=api_user, api_key=api_key)
    if jira is None:
        return None
    try:
        issue = jira.issue(id, fields=fields, expand=expand)
    except JIRAError as e:
        logger.error(f"Got an error: {e.status_code} {e.text}")
        return None
    return issue


def create_jira_issue(
    fields={}, api_server="https://jira.atlassian.com", api_user=None, api_key=None
):
    """creates a issue on the jira server

    :param fields: issue fields e.g) {'project': {'id': 123}, 'summary': 'New issue from jira-python', 'description': 'Look into this one', 'issuetype': {'name': 'Bug'}}
    :type fields: Dict[str, Any]
    :param api_server: jira api server url(default: https://jira.atlassian.com)
    :type api_server: str
    :param api_user: jira api user. If api_user is none, JIRA_API_USER environment value will be assigned.
    :type api_user: str
    :param api_key: jira user api key. If api_key is none, JIRA_API_KEY environment value will be assigned.
    :type api_key: str
    :return: `jira.Issue` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    jira = _get_client(api_server=api_server, api_user=api_user, api_key=api_key)
    if jira is None:
        return None
    try:
        issue = jira.create_issue(fields=fields)
    except JIRAError as e:
        logger.error(f"Got an error: {e.status_code} {e.text}")
        return None
    return issue


def create_jira_issues(
    issue_list=[], api_server="https://jira.atlassian.com", api_user=None, api_key=None
):
    """creates multiple issues on the jira server

    :param issue_list: issue list e.g) [{'project': {'id': 123}, 'summary': 'New issue from jira-python', 'description': 'Look into this one', 'issuetype': {'name': 'Bug'}}]
    :type fields: List[Dict[str, Any]]
    :param api_server: jira api server url(default: https://jira.atlassian.com)
    :type api_server: str
    :param api_user: jira api user. If api_user is none, JIRA_API_USER environment value will be assigned.
    :type api_user: str
    :param api_key: jira user api key. If api_key is none, JIRA_API_KEY environment value will be assigned.
    :type api_key: str
    :return: `jira.Issue` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    jira = _get_client(api_server=api_server, api_user=api_user, api_key=api_key)
    if jira is None:
        return None
    try:
        issues = jira.create_issues(field_list=issue_list)
    except JIRAError as e:
        logger.error(f"Got an error: {e.status_code} {e.text}")
        return None
    return issues


def update_jira_issue(
    jira_id,
    fields={},
    notify=True,
    api_server="https://jira.atlassian.com",
    api_user=None,
    api_key=None,
):
    """updates the issue on the jira server

    :param jira_id: jira id of the issue
    :type jira_id: str
    :param fields: issue fields e.g) {'summary': 'New issue from jira-python', 'description': 'Look into this one'}
    :type fields: Dict[str, Any]
    :param notify: should suppress notifications of the update
    :type notify: bool
    :param api_server: jira api server url(default: https://jira.atlassian.com)
    :type api_server: str
    :param api_user: jira api user. If api_user is none, JIRA_API_USER environment value will be assigned.
    :type api_user: str
    :param api_key: jira user api key. If api_key is none, JIRA_API_KEY environment value will be assigned.
    :type api_key: str
    :return: `jira.Issue` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    jira = _get_client(api_server=api_server, api_user=api_user, api_key=api_key)
    if jira is None:
        return None
    try:
        issue = jira.issue(jira_id)
        issue.update(fields=fields, notify=notify)
    except JIRAError as e:
        logger.error(f"Got an error: {e.status_code} {e.text}")
        return None
    return issue


def delete_jira_issue(
    jira_id,
    delete_subtasks=False,
    api_server="https://jira.atlassian.com",
    api_user=None,
    api_key=None,
):
    """deletes the issue on the jira server

    :param jira_id: jira id of the issue
    :type jira_id: str
    :param delete_subtasks: if the issue has subtasks, this argument must be set to true for the call to succeed.
    :type delete_subtasks: bool
    :param api_server: jira api server url(default: https://jira.atlassian.com)
    :type api_server: str
    :param api_user: jira api user. If api_user is none, JIRA_API_USER environment value will be assigned.
    :type api_user: str
    :param api_key: jira user api key. If api_key is none, JIRA_API_KEY environment value will be assigned.
    :type api_key: str
    :return: `True` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    jira = _get_client(api_server=api_server, api_user=api_user, api_key=api_key)
    if jira is None:
        return None
    try:
        issue = jira.issue(jira_id)
        issue.delete(deleteSubtasks=delete_subtasks)
    except JIRAError as e:
        logger.error(f"Got an error: {e.status_code} {e.text}")
        return None
    return True
