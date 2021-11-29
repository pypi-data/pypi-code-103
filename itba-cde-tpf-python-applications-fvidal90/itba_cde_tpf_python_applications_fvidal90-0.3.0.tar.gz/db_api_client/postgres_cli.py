from db_api_client.parent_cli import DBAPIClient


class PostgresClient(DBAPIClient):
    def __init__(self, user, password, host, port, database):
        db = f'//{user}:{password}@{host}:{port}/{database}'
        super().__init__('postgresql', db)


if __name__ == '__main__':
    pg_user = 'postgres'
    pg_password = 'postgres'
    pg_host = 'localhost'
    pg_port = 5432
    pg_database = 'stock'
    postgres_cli = PostgresClient(pg_user, pg_password, pg_host, pg_port, pg_database)
    print(postgres_cli.to_frame('SELECT * FROM stock_value'))
