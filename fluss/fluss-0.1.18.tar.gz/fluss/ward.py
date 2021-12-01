
from fakts.config.base import Config
from herre.wards.query import TypedQuery
from herre.wards.graphql import GraphQLWard


class FlussConfig(Config):
    host: str
    port: int
    secure: bool

    class Config:
       group = "fluss"

    @property
    def endpoint(self):
        return f"http://{self.host}:{self.port}/graphql"



class FlussWard(GraphQLWard):
    configClass = FlussConfig

    class Meta:
        key = "fluss"



async def open_playground():
    raise NotImplementedError("SSS")



class gql(TypedQuery):
    ward_key = "fluss"
    


