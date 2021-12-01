import json
import os
import sqlite3
from abc import ABC

DATATYPES = (
    "VARCHAR",
    "INT",
    "INTEGER",
    "TEXT",
    "NUMERIC",
    "REAL",
    "BLOB",
    "TINYINT",
    "SMALLINT",
    "MEDIUMINT",
    "BIGINT",
    "UNSIGNED BIG INT",
    "CHARACTER",
    "DOUBLE",
    "FLOAT",
    "DATETIME",
    "DATE",
    "BOOLEAN",
    "DECIMAL",
)

conn = sqlite3.connect(f"entertainment.db")
cur = conn.cursor()


class Field:
    def __init__(self, data_type, primary_key=False):
        if data_type.upper() not in DATATYPES:
            raise ValueError(f"Тип {data_type} не поддерживается")
        self.is_primary_key = primary_key
        self.data_type = data_type

    def __set_name__(self, obj, name: str):
        if self.is_primary_key:
            obj.pk = [name, None, self.data_type]
        else:
            obj.non_key_attributes.append((name, self.data_type))

        self.fetch = f'SELECT {name} FROM {obj.__name__ + "s"} WHERE {obj.pk[0]}=?;'
        self.store = f'UPDATE {obj.__name__ + "s"} SET {name}=? WHERE {obj.pk[0]}=?;'

    def __get__(self, obj, objtype=None):
        return cur.execute(self.fetch, [obj.pk[1]]).fetchone()[0]

    def __set__(self, obj, value):
        cur.execute(self.store, [value, obj.pk[1]])
        conn.commit()


class Row:
    def __set_name__(self, obj, name: str):
        self.remove = f'DELETE FROM {obj.__name__ + "s"} WHERE {obj.pk[0]}=?;'
        self.class_name = obj.__name__

    def __set__(self, obj, values: tuple):
        query = f"""
                    INSERT INTO {self.class_name + "s"} 
                    {obj.pk[0], *(attr for attr, datatype in obj.non_key_attributes)} VALUES {values};
                """
        obj.pk[1] = values[0]
        try:
            conn.execute(query)
            conn.commit()
        except Exception:
            print("Строка с таким pk уже существует в таблице")

    def __delete__(self, obj):
        try:
            cur.execute(self.remove, [obj.pk[1]])
            conn.commit()
        except Exception:
            print("Строки с таким pk нет в таблице")


class Model(ABC):
    non_key_attributes = []

    def __init__(self, *values):
        self.values = values


# class User(Model):
#     id = Field(data_type="INT", primary_key=True)
#     username = Field(data_type="VARCHAR")
#     surname = Field(data_type="VARCHAR")
#     age = Field(data_type="INT")
#     values = Row()


def makemigrations(migrations_path="migrations"):
    try:
        migration_files = os.listdir(migrations_path)
    except Exception:
        os.mkdir("migrations")
        migration_files = []
    tables = [cls for cls in Model.__subclasses__()]
    for table in tables:
        table_name = table.__name__ + "s"
        primary_key = table.__dict__["pk"]
        attrs_dict = {
            attr: datatype
            for attr, datatype in table.__base__.__dict__["non_key_attributes"]
        }
        new_file_number = (
            int(migration_files[-1].rstrip(".json")) + 1
            if len(migration_files) > 0
            else 1
        )

        with open(f"migrations/{new_file_number}.json", "a") as f:
            to_json = {
                table_name: {
                    "PRIMARY KEY": [primary_key[0], primary_key[2]],
                    **attrs_dict,
                }
            }
            f.write(json.dumps(to_json))


def open_migrations_files(migration_files) -> tuple:
    try:
        with open(f"migrations/{migration_files[-2]}", "r") as f:
            tables_to_delete = json.load(f)
    except Exception:
        tables_to_delete = None
    with open(f"migrations/{migration_files[-1]}", "r") as f:
        tables_to_create = json.load(f)

    return tables_to_delete, tables_to_create


def migrate_base(is_migrate: bool, migrations_path: str) -> None:
    migration_files = os.listdir(migrations_path)
    if is_migrate:
        tables_to_delete, tables_to_create = open_migrations_files(migration_files)
    else:
        tables_to_create, tables_to_delete = open_migrations_files(migration_files)
    if tables_to_delete:
        for table in tables_to_delete:
            drop_query = f"DROP TABLE {table};"
            try:
                cur.execute(drop_query)
                conn.commit()
            except Exception as e:
                print(e)
    if tables_to_create:
        for table in tables_to_create:
            primary_key = tables_to_create[table]["PRIMARY KEY"]
            attrs = ", ".join(
                [
                    attr + " " + datatype
                    for attr, datatype in [
                        (i, tables_to_create[table][i])
                        for i in tables_to_create[table]
                        if i != "PRIMARY KEY"
                    ]
                ]
            )
            create_query = f"""
                                CREATE TABLE {table} (
                                 {primary_key[0]} {primary_key[1]} PRIMARY KEY,
                                 {attrs}
                                );
                        """
            try:
                cur.execute(create_query)
                conn.commit()
            except Exception as e:
                print(e)
    if not is_migrate:
        os.remove(f"{migrations_path}/{migration_files[-1]}")


def migrate(migrations_path="migrations") -> None:
    migrate_base(is_migrate=True, migrations_path=migrations_path)


def downgrade(migrations_path="migrations") -> None:
    migrate_base(is_migrate=False, migrations_path=migrations_path)


if __name__ == "__main__":
    # makemigrations()
    # migrate()
    # downgrade()
    # m1 = User(1, "Челикслав", "Челикславов", 5)
    # m1.age = 15
    # print(m1.age)
    # del m1.values
    pass
