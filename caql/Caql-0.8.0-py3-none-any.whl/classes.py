from dataclasses import dataclass, field, asdict
from enum import Enum
from . import ty

SQL_OPERATORS = [
    "is_null",
    "is_not_null",
    "==",
    "eq",
    "!=",
    "ne",
    ">",
    "gt",
    "<",
    "lt",
    ">=",
    "ge",
    "<=",
    "le",
    "like",
    "ilike",
    "not_ilike",
    "in",
    "not_in",
    "any",
    "not_any",
]


@dataclass
class CackPredicate:
    op: str
    field: str
    value: ty.Union[str, int, bool, float, None]

    def __call__(self, model):
        field = getattr(model, self.field)
        if self.op == "is_null":
            return field.is_(None) == self.value
        elif self.op == "is_not_null":
            return field.isnot(None) == self.value
        elif self.op == "==" or self.op == "eq":
            return field == self.value
        elif self.op == "!=" or self.op == "ne":
            return field != self.value
        elif self.op == ">" or self.op == "gt":
            return field > self.value
        elif self.op == "<" or self.op == "lt":
            return field < self.value
        elif self.op == ">=" or self.op == "ge":
            return field >= self.value
        elif self.op == "<=" or self.op == "le":
            return field <= self.value
        elif self.op == "like":
            return field.like(self.value)
        elif self.op == "ilike":
            return field.ilike(self.value)
        elif self.op == "not_ilike":
            return ~field.ilike(self.value)
        elif self.op == "in":
            return field.in_(self.value)
        elif self.op == "~in":
            return ~field.in_(self.value)
        elif self.op == "any":
            return field.any(self.value)
        elif self.op == "not_any":
            return ~field.any(self.value)
        else:
            raise ValueError(f"Unknown op: {self.op}")


@dataclass
class CackQuery:
    """
    Attributes
    ----------

    source (str): The name of the table (for the top-most query) or field (for relations queries) to query.
    required (bool): Whether at least one result matching the query is expected. If True and no results are found
        for the top-most query, an error is raised. If True and the query is a relation, the parent of the relation
        will be removed from the result set. If False, the return value will depend on value of `return_list`.
        If `return_list` is True, an empty list will be returned. Otherwise, the return value will be `None`.
    fields (Optional[List[str]]):
        The fields to include in the result. If None, a server-defined default view will be returned.
    key (str):
        An identifier for the query. Will be attached to the result. Defaults to "".
    filters (Dict[str, Union[str, int, bool, float, None]]): Restrict results by equality checks. Defaults to {}.
    predicates (List[CackqlPredicate]): Optional list of more complex predicates to restrict results. Defaults to [].
    return_list (Optional[bool]):
        Whether to return the results as a list. Defaults to None, which means the behaviour is determined by the server,
        based on whether the attribute has a list value or not. If multiple results are
        present and `return_list` is `False`, the first result in the list is chosen.
    slice_from (Optional[int]):
        Start index for slicing results. Slicing is performed on the result set after ordering and before
        lists are converted to scalars (if `return_list` is False). Defaults to None, which has the same semantics as 0.
    slice_to (Optional[int]): End index for slicing results. Slicing is performed on the result set after ordering and before lists are
        converted to scalars (if `return_list` is False). Defaults to None, indicating no limit.
    slice_step (Optional[int]): Step for calculating the slice. Defaults to None, which has the same semantics as 1.

    Example
    -------

    [
        {
            "key": "it's a user!"
            "source": "User",
            "fields": ["id"],
            "filters": {},
            "relations": [
                {"key": "oh, a person!", "source": "person", "filter": {}, "fields": ["name", "email"]},
                {"key": "the org", "source": "org", "filter": {}, "fields": ["name"], "relations": []}
            ]
        }
    ]
    """

    source: str
    required: bool
    fields: ty.Optional[ty.List[str]] = None
    filters: ty.Dict[str, ty.Any] = field(default_factory=dict)  # type: ignore
    predicates: ty.List[CackPredicate] = field(default_factory=list)  # type: ignore
    relations: ty.List["CackQuery"] = field(default_factory=list)  # type: ignore
    key: str = ""
    return_list: ty.Optional[bool] = None
    slice_start: ty.Optional[int] = None
    slice_stop: ty.Optional[int] = None
    slice_step: ty.Optional[int] = None

    def dict(self):
        return asdict(self)


@dataclass
class CackResult:
    key: str
    fields: ty.Dict[str, ty.Any]
    relations: ty.List[ty.Union["CackResult", ty.List["CackResult"], None]] = field(
        default_factory=list
    )

    def dict(self):
        return asdict(self)
