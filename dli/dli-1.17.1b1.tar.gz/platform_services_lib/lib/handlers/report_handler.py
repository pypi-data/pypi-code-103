import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class ReportHandler:

    def __init__(self):
        self.report_host = os.environ.get("REPORTING_URL", "None")

    def report(
        self,
        statement: str,
        status: bool = True,
        dataset_shortcode: Optional[str] = None,
        modified: Optional[bool] = None,
        stage: Optional[str] = None,
        note1: Optional[str] = "",
        note2: Optional[str] = ""
    ):
        # only report 'stage' based things for a dataset or the process as a whole, not logs.
        # we don't want to know you're getting session details at a high level
        # e.g. beginning Unit Z, ending Unit Y
        status = "success" if status else "fail"
        level = "dataset" if dataset_shortcode is not None else "collector"
        modified = "yes" if modified else "no"
        if stage not in ["extract", "transform", "load", "validation"]:
            logger.warning('Stage is not set to extract / transform / load / validation')

        data = {
            "statement": statement,
            "modified": "no"
        }

        if dataset_shortcode:
            data["dataset"] = dataset_shortcode
            data["modified"] = modified
            data["note1"] = note1
            data["note2"] = note2

        try:
            if self.report_host != 'None':
                requests.post(
                    f"{self.report_host}/report/{stage}/{level}/{status}",
                    json=data,
                    timeout=0.5
                )
        except Exception as e:
            # back off and retry
            logger.debug("[crawler] Cannot report")

