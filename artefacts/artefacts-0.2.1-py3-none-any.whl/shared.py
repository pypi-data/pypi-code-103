from typing import Union
from pydantic import BaseModel


class Metadata(BaseModel):
    """
    Metadata associated with various artifacts.

    Attributes:

        schema_version (str):
            The artifact schema version of the artifact

        invocation_id (Union[str, None]):
            The invocation_id of the artifact

        env (dict):
            The DBT_* environment variables set when the artifact was generated

        generated_at (str):
            The timestamp when the artifact was generated

        dbt_version (str):
            The dbt_version of the artifact
    """

    class Config:
        extra = "ignore"

    dbt_schema_version: str
    dbt_version: str
    invocation_id: Union[str, None]
    env: dict
    generated_at: str

    @property
    def schema_version(self):
        return self.dbt_schema_version.split("/")[-1].replace(".json", "")
