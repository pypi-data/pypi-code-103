import asyncio
# import aiomysql
from typing import List, Tuple, Union, Any
from .connection import connect

class Mysql:
    def __init__(self,
                 host='127.0.0.1',
                 port=3306,
                 user='root',
                 password='root',
                 db='test') -> None:
        self.loop = asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.pool = None
        self.conn = None

    async def connect(self):
        """
        建立数据库连接
        """
        # self.conn = await aiomysql.connect(
        self.conn = await connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            loop=self.loop)

    async def execute(self,
                      sql: str = None,
                      data: List[Tuple] = None,
                      return_all=True) -> Union[Tuple[Tuple], Tuple[Any]]:
        """
        执行SQL语句
        """
        # 自动建立连接
        if self.conn is None:
            await self.connect()

        async with self.conn.cursor() as cur:
            # 批量新增
            if data is not None:
                try:
                    await cur.executemany(sql, data)
                    await self.conn.commit()
                except Exception as e:
                    await self.conn.rollback()
                    raise e
            else:
                # 执行单条SQL语句
                try:
                    await cur.execute(sql)
                    await self.conn.commit()
                except Exception as e:
                    await self.conn.rollback()
                    raise e

            # 返回数据
            if return_all:
                return await cur.fetchall()

            return await cur.fetchone()

    async def create_table(self, sql: str):
        """
        创建数据库表
        """
        await self.execute(sql)

    async def close(self):
        self.conn.close()