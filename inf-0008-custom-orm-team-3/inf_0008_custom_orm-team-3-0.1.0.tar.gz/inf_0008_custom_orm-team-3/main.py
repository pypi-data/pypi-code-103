import sqlite3


def connection(name):
    global conn
    conn = sqlite3.connect(name)
    cur = conn.cursor()
    return cur


class Field:
    def __init__(self, type_colum):
        self.type_colum = type_colum

    def __get__(self, obj, objtype=None):
        return self._value

    def __set__(self, obj, value):
        self._value = value


class Session:
    def __new__(cls, *args, **kwargs):
        column_names = [k for k, v in cls.__dict__.items() if isinstance(v, Field)]
        column_values = [v.type_colum for k, v in cls.__dict__.items() if isinstance(v, Field)]

        try:
            cursor.execute(f"CREATE TABLE {cls.__name__} "
                           f"( id INTEGER PRIMARY KEY,"
                           f" {', '.join([k + ' ' + v for k, v in zip(column_names, column_values)])});")
        except sqlite3.OperationalError:
            pass
        return super().__new__(cls)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def select(self):
        return cursor.execute(f"SELECT * FROM {self.__class__.__name__};")

    def save(self):
        column_names = [k for k, v in self.__class__.__dict__.items() if isinstance(v, Field)]
        column_values = [getattr(self, k) for k, v in self.__class__.__dict__.items() if isinstance(v, Field)]
        for i in range(len(column_values)):
            if isinstance(column_values[i], str):
                column_values[i] = f'"{column_values[i]}"'

        try:

            cursor.execute(f"UPDATE {self.__class__.__name__} SET "
                           f"{', '.join([k + '=' + str(v) for k, v in zip(column_names, column_values)])} "
                           f"WHERE id = {self.id};")
        except AttributeError:
            cursor.execute(f"INSERT INTO {self.__class__.__name__} ({', '.join(column_names)}) "
                           f"VALUES ({', '.join([str(i) for i in column_values])});")
            self.id = cursor.lastrowid
        finally:
            conn.commit()

    def delete(self):
        cursor.execute(f"DELETE FROM {self.__class__.__name__} WHERE id = {self.id};")
        conn.commit()


cursor = connection("entertainment.db")
