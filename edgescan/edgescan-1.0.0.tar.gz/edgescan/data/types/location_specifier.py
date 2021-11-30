from dataclasses import dataclass
from edgescan.data.types.object import Object

IP = 'ip'
CIDR = 'cidr'
BLOCK = 'block'


@dataclass(frozen=True)
class LocationSpecifier(Object):
    id: int
    location: str
    location_type: str

    def is_ip(self) -> bool:
        return self.location_type == IP

    def is_ip_range(self) -> bool:
        return self.location_type == BLOCK

    def is_cidr(self) -> bool:
        return self.location_type == CIDR

    def __hash__(self):
        return self.id
