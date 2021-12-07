from jsonpath_ng.ext import parse


def match(query, document):
    """Поиск в докумене по json-path селектору.

    :param query: json-path селектор
    :param document: документ к которому применяется json-path селектор
    """
    result = parse(query).find(document)
    return [i.value for i in result]


def match_smart(query, document):
    """Поиск в докумене по json-path селектору.

    :param query: json-path селектор
    :param document: документ к которому применяется json-path селектор

    Во многих реализациях jsonpath, он всегда результат поиска возвращает в виде списка,
    что не очень удобно в использовании в ассертах (дополнительно приходится вынимать нулевой
    элемент из списка). Поэтому в этой функции для тех случаев когда никак не может найтись несколько
    вариантов - сразу возвращается значение из списка.
    """
    result = match(query, document)
    if len(result) > 1 or ':' in query or '..' in query or '?' in query:
        return result
    else:
        return result[0]
