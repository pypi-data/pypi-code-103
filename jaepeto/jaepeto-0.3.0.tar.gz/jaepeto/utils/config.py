"""
Parse user config
"""
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Union


def parse_config(config_file: Union[Path, str]):
    config = ConfigParser()
    config.read(config_file)

    project_name = config.get("project", "name")
    project_name = project_name if project_name else "Project"

    project_info = {
        "name": project_name,
        "description": config.get("project", "description"),
        "src": config.get("project", "srcdir"),
        "doc_dir": config.get("docs", "docdir"),
    }

    os.environ["JAEPETO_API_KEY"] = config.get("project", "api_key")
    os.environ["JAEPETO_PROJECT_NAME"] = project_name

    language = config.get("project", "language")

    if language.lower().strip().rstrip("3") != "python":
        raise RuntimeError(
            f"""Jaepeto currently only works
        on Python (3), not {language}"""
        )

    # Documentation
    project_info["docs"] = {"technical": True, "technical_name": "technical_doc"}

    # Issues
    if config.has_section("issues"):
        issue_service = config.get("issues", "integration")
        if issue_service and issue_service.lower() != "github":
            project_info["issues"] = {}
        else:
            try:
                username = config.get("issues", "username")
                repo = config.get("issues", "repo")
            except:
                project_info["issues"] = {}
            else:
                project_info["issues"] = {"username": username, "repo": repo}
    else:
        project_info["issues"] = {}

    return project_info
