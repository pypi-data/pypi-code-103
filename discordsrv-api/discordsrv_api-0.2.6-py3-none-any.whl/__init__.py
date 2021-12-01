from discordsrv_api.models import *


class User:
    def __init__(
        self,
        db,
        link,
        discord,
        uuid) -> None:
        self.db = db
        self.uuid = uuid
        self.link = link
        self.discord = discord


class DiscordSRV:
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

    def get_discord(self, uuid: str):
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
                link=result[0],
                discord=result[1],
                uuid=result[2])
    
    def get_uuid(self, discord: str):
        if not self.db.is_connected:
            self.db.reconnect()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{self.columns.table}` WHERE `{self.columns.discord}` = %s",
                [discord],
            )
            result = cursor.fetchall()
            result = result[0]
            return User(
                db=self,
                link=result[0],
                discord=result[1],
                uuid=result[2])

    def set_discord(self, uuid: str, discord: str):
        if not self.db.is_connected:
            self.db.reconnect()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.columns.table} SET discord=%s WHERE {self.columns.uuid}=%s",
                [discord, uuid],
            )
            self.db.commit()

    def delete_discord(self, uuid: str):
        if not self.db.is_connected:
            self.db.reconnect()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {self.columns.table} WHERE {self.columns.uuid}=%s",
                [uuid],
            )
            self.db.commit()

    def create_discord(self, uuid: str, discord: str):
        if not self.db.is_connected:
            self.db.reconnect()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {self.columns.table}({self.columns.uuid},{self.columns.discord}) VALUES(%s,%s)",
                [uuid, discord],
            )
            self.db.commit()
