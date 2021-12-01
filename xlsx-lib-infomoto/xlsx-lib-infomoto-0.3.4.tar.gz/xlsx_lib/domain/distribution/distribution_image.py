from io import BytesIO

from camel_model.camel_model import CamelModel


class DistributionImage(CamelModel):
    name: str
    format: str
    file: BytesIO

