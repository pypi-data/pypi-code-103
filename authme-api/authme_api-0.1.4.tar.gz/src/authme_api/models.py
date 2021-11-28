from dataclasses import dataclass
import mysql.connector


@dataclass
class Columns:
    Id: str = "id"
    Name: str = "username"
    RealName: str = "realname"
    Password: str = "password"
    Salt: str = ""
    Email: str = "email"
    Logged: str = "isLogged"
    HasSession: str = "hasSession"
    totpKey: str = "totp"
    Ip: str = "ip"
    LastLogin: str = "lastlogin"
    RegisterDate: str = "regdate"
    RegisterIp: str = "regip"
    locX: str = "x"
    locY: str = "y"
    locZ: str = "z"
    locWorld: str = "world"
    locYaw: str = "yaw"
    locPitch: str = "pitch"
    PlayerUUID: str = ""
    table: str = "authme"


@dataclass
class DB:
    user: str
    password: str
    host: str
    name: str
    port: int = 3306

    def __post_init__(self):
        self.database = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.name,
            port=self.port,
        )
