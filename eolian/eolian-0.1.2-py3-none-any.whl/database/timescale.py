import logging

from peewee import PostgresqlDatabase


class Timescale(PostgresqlDatabase):
    def is_active(self):
        res = self.execute_sql("select 1 as test_connection")
        pg_db_active = res and str(res.fetchall()) == "[(1,)]"

        return pg_db_active

    def insert(self, model, data):
        with self.atomic() as transaction:
            try:
                # https://docs.peewee-orm.com/en/latest/peewee/querying.html
                model.insert(data).on_conflict(action="ignore").execute()
            except Exception as e:
                transaction.rollback()
                logging.error(
                    "Exception happened while trying to save the data:", exc_info=True
                )
