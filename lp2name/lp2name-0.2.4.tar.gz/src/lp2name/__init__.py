from lp2name.models import *
from json import loads


class User:
    def __init__(
        self,
        db,
        uuid,
        username) -> None:
        self.db = db
        self.uuid = uuid
        self.username = username
    
    def __str__(self) -> str:
        return self.uuid + '=' + self.username

class Permission:
    def __init__(self, uuid, permission, value, server, world, expiry, contexts) -> None:
        self.uuid = uuid
        self.permission = permission
        self.value = value
        self.server = server
        self.world = world
        self.expiry = expiry
        self.contexts = loads(contexts)
    
    def __str__(self) -> str:
        return self.uuid + '=' + self.permission


class LuckPerms:
    def __init__(
        self,
        database: DB,
        columns: Columns = Columns(),
    ):
        self.db = database.database
        self.columns = columns
        self.model: list[str] = []
        self.describe_table()

    def describe_table(self):
        if not self.db.is_connected:
            self.db.reconnect()
        with self.db.cursor() as cursor:
            cursor.execute(f"DESCRIBE {self.columns.table}")
            result = cursor.fetchall()
            for i in result:
                self.model.append(i[0])

    def get_user_by_name(self, name: str):
        if not self.db.is_connected:
            self.db.reconnect()
        name = name.lower()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{self.columns.table}` WHERE `{self.columns.username}` = %s",
                [name],
            )
            result = cursor.fetchall()
            result = result[0]
            return User(
                db=self,
                uuid=result[0],
                username=name)
    
    def get_user_by_uuid(self, uuid: str):
        if not self.db.is_connected:
            self.db.reconnect()
        uuid = uuid.lower()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{self.columns.table}` WHERE `{self.columns.uuid}` = %s",
                [uuid],
            )
            result = cursor.fetchall()
            result = result[0]
            return User(
                db=self,
                uuid=uuid,
                username=result[1])
    
    def get_user_permissions(self, uuid: str):
        if not self.db.is_connected:
            self.db.reconnect()
        uuid = uuid.lower()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{self.columns.table_permissions}` WHERE `{self.columns.uuid}` = %s",
                [uuid],
            )
            result = cursor.fetchall()
            out = []
            for i in result:
                out.append(Permission(uuid=i[1], permission=i[2], value=i[3], server=i[4], world=i[5], expiry=i[6], contexts=i[7]))
        return out
