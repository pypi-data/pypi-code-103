from typing import List, Optional

from camel_model.camel_model import CamelModel


class DistributionData(CamelModel):
    distribution_title: Optional[str]
    distribution_text: List[str] = []
