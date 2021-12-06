import typing as T
from dgraph_orm import Node

StrawberryType = T.TypeVar("StrawberryType")
NodeType = T.TypeVar("NodeType", bound=Node)


class Display(T.Generic[NodeType]):
    @classmethod
    def from_node(cls: T.Type[StrawberryType], node: NodeType) -> StrawberryType:
        fields_to_use = set(cls.__dataclass_fields__.keys()) & set(
            node.__fields__.keys()
        )
        straw = cls(**node.dict(include=fields_to_use))
        straw._node = node
        return straw

    @classmethod
    def from_node_or_none(
        cls: T.Type[StrawberryType], node: T.Optional[NodeType]
    ) -> T.Optional[StrawberryType]:
        if node is None:
            return None
        return cls.from_node(node=node)

    @classmethod
    def from_nodes(
        cls: T.Type[StrawberryType], nodes: T.List[NodeType]
    ) -> T.List[StrawberryType]:
        return [cls.from_node(node) for node in nodes]

    @property
    def node(self) -> NodeType:
        return self._node


DBType = T.TypeVar("DBType", bound=Node)
LayerNodeType = T.TypeVar("LayerNodeType", bound=Node)

# TODO prob rename this...
class Node(T.Generic[DBType]):
    @classmethod
    def from_db(cls: T.Type[LayerNodeType], model_db: DBType) -> LayerNodeType:
        # TODO make sure this covers everything
        # but must also transfer private fields and cache!
        n = cls(**model_db.dict())
        # for all private fields too
        for private_field in model_db.__private_attributes__.keys():
            setattr(n, private_field, getattr(model_db, private_field))
        return n

    @classmethod
    def from_db_or_none(
        cls: T.Type[LayerNodeType], model_db: T.Optional[DBType]
    ) -> T.Optional[LayerNodeType]:
        if not model_db:
            return None
        return cls.from_db(model_db)

    @classmethod
    def from_dbs(
        cls: T.Type[LayerNodeType], model_dbs: T.List[DBType]
    ) -> T.List[LayerNodeType]:
        return [cls.from_db(model_db) for model_db in model_dbs]
