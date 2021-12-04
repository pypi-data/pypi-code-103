"""
Обработка QuerySet.
"""
import sqlparse
from django.shortcuts import _get_queryset


def quick_pagination(queryset, page, limit, max_limit=1000):
    """
    Функция быстрой паджинации для больших таблиц, не вызывающая count(*).
    """
    try:
        page = int(page)
    except ValueError:
        page = 1
    try:
        limit = int(limit)
        assert limit <= max_limit
    except ValueError:
        limit = 10
    except AssertionError:
        limit = max_limit
    offset = (page - 1) * limit
    queryset = queryset[offset:(offset + limit + 1)]
    result = queryset
    if len(result) > limit:
        has_next = True
        result = result[:limit]
    else:
        has_next = False
    return result, page, limit, has_next


def dictfetchall(cursor, aggregate=()):
    """
    Return all rows from a cursor as a dict.
    """
    columns = [col[0] for col in cursor.description]

    total = {col: 0 for col in aggregate}
    use_total = bool(total)
    total_keys = total.keys()

    def to_dict(row):
        d = dict(zip(columns, row))
        if use_total:
            for col in total_keys:
                total[col] += d[col]
        return d

    objects = [to_dict(row) for row in cursor.fetchall()]
    if total:
        return objects, total
    return objects


def get_object_or_none(klass, *args, **kwargs):
    """
    Возвращает объект или None, если объект не существует.

    klass может быть Model, Manager, или объектом QuerySet. Все остальные
    переданные параметры используются для запроса get().

    Замечание: Возвращает None, если найдено более одного объекта.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    except queryset.model.MultipleObjectsReturned:
        return None


def pretty_sql(queryset):
    """Форматирует QuerySet в человекочитаемый SQL."""
    query = queryset.query
    compiler = query.get_compiler(queryset.db)
    with compiler.connection.schema_editor() as editor:
        sql, params = compiler.as_sql()
        value = sql % tuple(editor.quote_value(p) for p in params)
    return sqlparse.format(value, reindent=True, keyword_case='upper')
