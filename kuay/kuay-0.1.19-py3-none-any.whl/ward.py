from fakts import Config
from herre.wards.query import TypedQuery
from herre.wards.graphql import GraphQLWard


class PortConfig(Config):
    host: str
    port: int
    secure: bool

    class Config:
        group = "port"
        env_prefix = "port_"

    @property
    def endpoint(self):
        return f"http://{self.host}:{self.port}/graphql"


class PortWard(GraphQLWard):
    configClass = PortConfig

    class Meta:
        key = "port"


class gql(TypedQuery):
    ward_key = "port"
