from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


@dataclass
class SSOMetadataDTO(DataClassJsonMixin):
    saml_metadata_file: str
    entity_id: str
    acs: str
