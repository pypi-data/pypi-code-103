from django.contrib import admin
from sqlalchemy.engine import create_engine
import urllib

# Register your models here.
class StgTable:
    """Classe para baixar dados de um banco e escrever em um outro,
    carregando uma tabela para uma tabela.
    """

    def __init__(
        self,
        table_name: str,
        cols: dict,
        cutoff_date_table: dict = None,
        cutoff_cols: dict = [],
        query: str = "",
    ):
        self.table_name = table_name
        self.cols = cols
        self.cutoff_date_table = cutoff_date_table
        self.cutoff_cols = cutoff_cols
        self.query = query

    def __str__(self):
        return f"StgTable({self.table_name}, {self.cols}, {self.cutoff_date_table}, {self.cutoff_cols})"

    def construct_query(self, cutoff_date=None, limit_date=None):
        """Constrói a query que pega as linhas de interesse para a stg."""

        if not self.query:
            self.query = f"SELECT {', '.join(self.cols)} FROM {self.table_name}"
        else:
            self.query = f"SELECT * FROM ({self.query}) a"

        where = None
        for col in self.cutoff_cols:
            if where:
                self.query += " OR "
            else:
                self.query += " WHERE "

            if not cutoff_date:
                cutoff_date = "1900-01-01"
            where = f"(CAST({col} as DATE) >= CAST('{cutoff_date}' as DATE)"

            if limit_date:
                where += f"AND CAST({col} as DATE) <= CAST('{limit_date}' as DATE)"

            where += ")"

            self.query += where

        return self.query
