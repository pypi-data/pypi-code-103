from enum import Enum


class OutputFormat(str, Enum):
    TEXT = 'text'
    JSON = 'json'
    JUNIT = 'junit'
    JSON_GITLAB_SAST = 'json-gitlab-sast'
    SARIF = 'sarif'
