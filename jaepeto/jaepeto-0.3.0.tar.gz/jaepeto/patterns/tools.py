"""
Third-party tools
e.g., Coverage, Docker
"""
import os
import re
from pathlib import Path
from typing import List, Optional

import requests

from jaepeto.utils import post


class ContainerParser:
    def __init__(self) -> None:
        self.file: Optional[str] = None

    def parse(self, project_dir: Path) -> Optional[str]:
        for spelling in ("dockerfile", "Dockerfile", "DOCKERFILE"):
            if spelling not in os.listdir(project_dir):
                continue

            self.file = spelling

            with open(project_dir / spelling, "r") as file:
                docker_contents = file.readlines()

            return post("parse-container", docker_contents)
        return None


class CIParser:
    def __init__(self) -> None:
        self.ci: List[str] = []

    def parse(self, project_dir: Path) -> str:
        ci_files = {
            "Travis": [".travis.yml", "travis.yml", ".travis.yaml", "travis.yaml"],
            "GitHub Actions": [f".github{os.sep}workflows"],
            "Circle CI": [f".circleci{os.sep}config.yml"],
            "GitLab CI": [".gitlab-ci.yml"],
        }

        for ci_provider, file_names in ci_files.items():
            for file in file_names:
                if (project_dir / file).exists():
                    self.ci.append(ci_provider)
                    break

    def __str__(self) -> str:
        if self.ci:
            if len(self.ci) == 1:
                arch = f"The project uses {self.ci[0]} for CI/CD."
            else:
                arch = (
                    f"The project uses multiple CI/CD providers: {', '.join(self.ci)}"
                )
        else:
            arch = "No CI/CD config files were detected."

        return arch
