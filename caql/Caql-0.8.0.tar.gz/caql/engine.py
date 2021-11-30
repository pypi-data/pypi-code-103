import json
from . import ty
from . import errors
from .classes import CackQuery, CackResult

try:
    import sqlalchemy.orm
except ImportError:  # pragma: no cover
    sqlalchemy = None


def query(
    db: ty.Session,
    cq: CackQuery,
    models: ty.Dict[str, ty.ModelType],
    authorize: ty.Callable[[ty.Any], bool],
) -> ty.Union[CackResult, ty.List[CackResult], None]:
    if sqlalchemy is not None and isinstance(db, sqlalchemy.orm.Session):
        return query_sqlalchemy(db, cq, models, authorize)
    else:
        raise NotImplementedError("Only sqlalchemy currently implemented")


def query_sqlalchemy(
    db: ty.Session,
    cq: CackQuery,
    models: ty.Dict[str, ty.ModelType],
    authorize: ty.Callable[[ty.Any], bool],
) -> ty.Union[CackResult, ty.List[CackResult], None]:
    table = models[cq.source]
    query = db.query(table).filter(*[p(table) for p in cq.predicates])
    objects = query.all()
    results = []
    for obj in objects:
        maybe_result = _maybe_make_result(cq, obj, authorize)
        if maybe_result is not None:
            results.append(maybe_result)
    results = _slice_results(results, cq)
    if cq.required and not results:
        raise errors.CackNotFound(json.dumps(cq.dict(), indent=2))
    if cq.return_list:
        return results
    elif results:
        return results[0]
    else:
        return None


_T = ty.TypeVar("_T")


def _slice_results(results: ty.List[_T], cq: CackQuery) -> ty.List[_T]:
    return results[slice(cq.slice_start, cq.slice_stop, cq.slice_step)]


def _maybe_make_result(
    cq: CackQuery, obj: ty.BaseModel, authorize: ty.Callable[[ty.BaseModel], bool]
) -> ty.Optional[CackResult]:
    if not authorize(obj):
        return None
    elif not _matches_filters(obj, cq.filters):
        return None
    relations = []
    for relation in cq.relations:
        maybe_result = _maybe_make_relation_results(relation, obj, authorize)
        if relation.required and not maybe_result:
            return None
        else:
            relations.append(maybe_result)
    return CackResult(
        key=cq.key, fields={k: getattr(obj, k) for k in cq.fields}, relations=relations
    )


def _maybe_make_relation_results(
    relation: CackQuery, obj: ty.BaseModel, authorize: ty.Callable[[ty.BaseModel], bool]
) -> ty.Union[CackResult, ty.List[CackResult], None]:
    if relation.predicates:
        raise NotImplementedError("Predicates currently only available on outer query")
    attr = getattr(obj, relation.source)
    values = attr if isinstance(attr, list) else [attr]
    values = [
        v for v in values if authorize(v) and _matches_filters(v, relation.filters)
    ]
    values = _slice_results(values, relation)
    maybe_results = [_maybe_make_result(relation, v, authorize) for v in values]
    results = [r for r in maybe_results if r is not None]
    if _get_return_list(relation.return_list, attr):
        return results
    elif results:
        return results[0]
    else:
        return None


def _get_return_list(
    return_list: ty.Optional[bool], attr: ty.Union[ty.List, ty.BaseModel]
) -> bool:
    """Handle smart default for return_list: if it's None, check whether the attribute
    is a list.
    """
    if return_list is not None:
        return return_list
    elif isinstance(attr, list):
        return True
    else:
        return False


def _matches_filters(
    obj: ty.BaseModel,
    filters: ty.Dict[str, ty.Union[str, int]],
) -> bool:
    return all(_is_equal(getattr(obj, key), value) for key, value in filters.items())


def _is_equal(x: ty.Any, y: ty.Any) -> bool:
    if isinstance(x, ty.UUID) or isinstance(y, ty.UUID):
        return str(x) == str(y)
    else:
        return x == y
