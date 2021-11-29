from db_api_client.parent_cli import DBAPIClient


class SqLiteClient(DBAPIClient):
    def __init__(self, db):
        super().__init__('sqlite', db)


if __name__ == '__main__':
    sqlite_db = '////tmp/sqlite_default.db'
    sqlite_cli = SqLiteClient(sqlite_db)
    print(sqlite_cli.to_frame('SELECT * FROM stocks_daily'))
