def aggregate_match(diccionario: dict) -> dict:
    return {'$match': diccionario}


def aggregate_group(diccionario: dict) -> dict:
    return {'$group': diccionario}


def aggregate_project(diccionario: dict) -> dict:
    return {'$project': diccionario}


def aggregate_unwind(valor: str) -> dict:
    return {'$unwind': valor}


def aggregate_sort(diccionario: dict) -> dict:
    return {'$sort': diccionario}


def mongo_lower(valor: str) -> dict:
    return {'$toLower': valor}


def mongo_push(valor: dict) -> dict:
    return {'$push': valor}


def mongo_upper(valor: str) -> dict:
    return {'$toUpper': valor}


def mongo_avg(valor: str) -> dict:
    return {'$avg': valor}


def mongo_sum(valor: int) -> dict:
    return {'$sum': valor}


def mongo_in(valor: list) -> dict:
    return {'$in': valor}


def mongo_nin(valor: list) -> dict:
    return {'$nin': valor}


def mongo_gt(valor: int) -> dict:
    return {'$gt': valor}


def mongo_gte(valor: int) -> dict:
    return {'$gte': valor}


def mongo_lt(valor: list) -> dict:
    return {'$lt': valor}


def mongo_and(valor: list) -> dict:
    return {'$and': valor}


def mongo_or(valor: list) -> dict:
    return {'$or': valor}


def mongo_concat(valor: list) -> dict:
    return {'$concat': valor}


def mongo_exists(existe: bool = True) -> dict:
    return {'$exists': existe}