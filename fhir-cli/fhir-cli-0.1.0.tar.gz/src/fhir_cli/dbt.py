import glob
import os
import re
import shutil
import subprocess  # nosec
from os.path import basename
from pathlib import Path

from fhir_cli import (
    CDM_LIST,
    DBT_INCREMENTAL_MODEL_TEMPLATE,
    DBT_MODELS_DIR,
    DBT_REF_PATTERN,
    JINJA_ENV,
    MAPPING_DIR,
)


def resolve_references(content: str) -> str:
    return re.sub(DBT_REF_PATTERN, "\\1{{ref('\\2')}}\\3", content, flags=re.IGNORECASE)


class Dbt:
    """The dbt command manages your DBT project"""

    @staticmethod
    def compile(incremental: bool = False):
        """The compile command creates the DBT models folder including all files in
        the schemas folder. It then compiles the sql files into DBT models by resolving
        DBT references and adding model configurations if needed.

        Args:
            incremental (bool): when True, the DBT models are configured to be incremental
        """
        if os.path.exists(DBT_MODELS_DIR):
            shutil.rmtree(DBT_MODELS_DIR)
        shutil.copytree(MAPPING_DIR, DBT_MODELS_DIR)

        for file_path in glob.iglob(f"{MAPPING_DIR}/**/*.sql", recursive=True):
            with open(file_path, "r") as f:
                with open(
                    f"{DBT_MODELS_DIR}{file_path.removeprefix(MAPPING_DIR)}", "w"
                ) as model_file:
                    output = f.read()
                    output = resolve_references(output)
                    parent_folder = basename(Path(file_path).parent)
                    if incremental and parent_folder in CDM_LIST:
                        output = JINJA_ENV.get_template(DBT_INCREMENTAL_MODEL_TEMPLATE).render(
                            stmt=output, target_schema=parent_folder
                        )
                    model_file.write(output)

    def run(self, incremental: bool = False):
        """The run command compiles the sql files then runs DBT

        Args:
            incremental (bool): when True, make the DBT models incremental
        """
        self.compile(incremental)
        subprocess.run(["dbt", "run", "--fail-fast"], env=os.environ.copy())  # nosec

    def refresh(self):
        """The refresh command refreshes DBT incremental models"""
        self.compile(True)
        subprocess.run(["dbt", "run", "--fail-fast --full-refresh"], env=os.environ.copy())  # nosec

    @staticmethod
    def test():
        """The test command run your DBT tests"""
        subprocess.run(["dbt", "test"], env=os.environ.copy())  # nosec

    @staticmethod
    def seed():
        """The seed command run your DBT seeds"""
        subprocess.run(["dbt", "seed"], env=os.environ.copy())  # nosec
