from authme_api.hash_types.sha256 import SHA256
from authme_api.hash_types import HashType
from authme_api.models import *


def find_hash_type(hash_str: str) -> HashType:
    mapping = {"SHA": SHA256}
    spl = hash_str.split("$")
    return mapping[spl[1]]


class User:
    def __init__(
        self,
        db,
        _id,
        username,
        password,
        ip,
        lastlogin,
        x,
        y,
        z,
        world,
        regdate,
        regip,
        isLogged,
        hasSession,
        totp=None,
    ) -> None:
        self.db = db
        self._id = (_id,)
        self.username = username
        hash_type = find_hash_type(password)
        self.password: HashType = hash_type.process_hash_str(password)
        self.ip = ip
        self.lastlogin = lastlogin
        self.x = x
        self.y = y
        self.z = z
        self.world = world
        self.regdate = regdate
        self.regip = regip
        self.isLogged = isLogged
        self.hasSession = hasSession
        self.totp = totp

    def verify_password(self, password):
        return self.password.is_equal(password)

    def change_password(self, new_password: str):
        self.password.change_password(new_password)
        with self.db.db.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.db.columns.table} SET {self.db.columns.Password}=%s WHERE {self.db.columns.Name}=%s",
                [self.password.get_hash_str(), self.username],
            )
            self.db.db.commit()
    
    def disable_2fa(self):
        with self.db.db.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.db.columns.table} SET {self.db.columns.totpKey}=NULL WHERE {self.db.columns.Name}=%s",
                [self.username],
            )
            self.db.db.commit()


class AuthMe:
    def __init__(
        self,
        database: DB,
        default_hash: HashType = SHA256,
        columns: Columns = Columns(),
    ):
        self.db = database.database
        self.default_hash = default_hash
        self.columns = columns
        self.model: list[str] = []
        self.describe_table()

    def describe_table(self):
        with self.db.cursor() as cursor:
            cursor.execute(f"DESCRIBE {self.columns.table}")
            result = cursor.fetchall()
            for i in result:
                self.model.append(i[0])

    def get_user_by_name(self, name: str):
        name = name.lower()
        with self.db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{self.columns.table}` WHERE `{self.columns.Name}` = %s",
                [name],
            )
            result = cursor.fetchall()
            result = result[0]
            return User(
                db=self,
                _id=result[0],
                username=result[1],
                password=result[3],
                ip=result[4],
                lastlogin=result[5],
                x=result[6],
                y=result[7],
                z=result[8],
                world=result[9],
                regdate=result[10],
                regip=result[11],
                isLogged=result[12],
                hasSession=result[13],
                totp=result[17],
            )
