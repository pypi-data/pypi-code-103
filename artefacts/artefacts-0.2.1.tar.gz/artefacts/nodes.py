from pydantic import BaseModel
from artefacts.mixins import NodeContextReader


class NodeUniqueId(str):
    def __init__(self, value):
        self.value = value

    @property
    def node_type(self):
        return self.value.split(".")[0]


class BaseNode(NodeContextReader, BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if "unique_id" not in v:
            raise TypeError(f"Object {v} has no key unique_id")

        unique_id = NodeUniqueId(v["unique_id"])

        if unique_id.node_type == "model":
            return Model(**v)
        elif unique_id.node_type == "test":
            return Test(**v)
        elif unique_id.node_type == "source":
            return Source(**v)
        elif unique_id.node_type == "seed":
            return Seed(**v)
        elif unique_id.node_type == "macro":
            return Macro(**v)
        else:
            return UndefinedNodeType(**v)

    unique_id: NodeUniqueId

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    def __hash__(self):
        return hash(self.unique_id)

    def __str__(self):
        return f"<{self.__class__.__name__} {self.unique_id}>"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)


class BaseNodeReference(NodeContextReader):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("NodeReferences must be strings")
        else:
            return cls(v)

    def __init__(self, unique_id):
        self.unique_id = unique_id

    def __str__(self):
        return self.unique_id

    def __repr__(self):
        return f"<NodeReference {self.unique_id}>"

    def __hash__(self):
        return hash(self.unique_id)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Model(BaseNode):
    pass


class Test(BaseNode):
    pass


class Seed(BaseNode):
    pass


class Source(BaseNode):
    pass


class Macro(BaseNode):
    pass


class UndefinedNodeType(BaseNode):
    pass
