from . import ty
from .classes import CackResult, CackQuery, CackPredicate
from . import engine


def query_collapsed(query: ty.Dict) -> ty.Dict:
    cq = transform_query(query)
    cr = engine.query(cq)
    return transform_result(cr)


def transform_query(collapsed: ty.Dict) -> CackQuery:
    key, value = collapsed.items()[0]
    fields = [f for f in value["fields"] if not isinstance(f, dict)]
    relations = [f for f in value["fields"] if isinstance(f, dict)]
    return CackQuery(key=key, source=value["source"], filters=value["filters"], fields=fields, relations=[transform_query(r) for r in relations], required=value["required"])

def transform_result(
    result: ty.Union[None, CackResult, ty.List[CackResult]]
) -> ty.Dict:
    if result is None or result == []:
        return {None: None}
    elif isinstance(result, list):
        ((key, value),) = transform_result(result[0]).items()
        return {key: [value] + [transform_result(r)[key] for r in result[1:]]}
    else:
        fields = dict(result.fields)
        for relation in result.relations:
            ((key, value),) = transform_result(relation).items()
            if key is not None:
                fields[key] = value  # type: ignore
        return {result.key: fields}
