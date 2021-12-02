from kigo.etl.mapper.keys import Key
import kigo.etl.mapper.typeof as typeof


class SQLArchetype:
    def __init__(self, table=None, field=None):
        self.sql_table = table
        self.sql_field = field

class Archetype:

    def __init__(self, typeof: typeof.Generic = None, key: Key=None, reference = None, constraint=None):
        self.typeof = typeof
        self.key = key
        self.constraint = constraint
        self.reference = reference
        self.__sql = None

    def get_sql(self):
        return self.__sql

    def sql(self, table=None, field=None):
        self.__sql = SQLArchetype(table, field)
        return self
