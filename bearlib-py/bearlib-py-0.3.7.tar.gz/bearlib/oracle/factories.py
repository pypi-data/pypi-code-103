from collections import namedtuple


def named_tuple_factory(cursor):
    """
    Returns a named tuple when querying
    Usage: `cursor.rowfactory = named_tuple_factory(cursor)`
    """
    column_names = [d[0].lower() for d in cursor.description]
    row = namedtuple("Row", column_names)
    return row


def dict_factory(cursor):
    """
    Returns a dictionary when querying
    Usage: `cursor.rowfactory = dict_factory(cursor)`
    """
    column_names = [d[0].lower() for d in cursor.description]

    def create_row(*args):
        return dict(zip(column_names, args))

    return create_row
