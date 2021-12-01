from dataclasses import dataclass
import mysql.connector
from mysql.connector.connection import MySQLConnection


@dataclass
class Columns:
    link: str = "link"
    discord: str = "discord"
    uuid: str = "uuid"
    table: str = "discordsrv_accounts"


@dataclass
class DB:
    user: str
    password: str
    host: str
    name: str
    port: int = 3306

    def __post_init__(self):
        self.database: MySQLConnection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.name,
            port=self.port,
        )
