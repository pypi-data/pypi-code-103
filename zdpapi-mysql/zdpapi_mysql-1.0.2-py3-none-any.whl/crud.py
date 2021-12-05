from .mysql import Mysql
from typing import Dict, List, Any, Tuple


class Crud:
    def __init__(self,
                 db: Mysql,
                 table: str,
                 columns: List[Any]) -> None:
        self.db = db
        self.table = table
        self.columns = columns

    def _get_columns_str(self):
        """
        根据列名自动生成names和values，用于动态拼接SQL语句
        """
        names = ", ".join(self.columns)
        values_ = ["%s" for i in range(len(self.columns))]
        values = ", ".join(values_)
        return names, values

    def _get_columns_id_str(self, columns: List) -> str:
        """
        返回字段字符串，用跟在select后面做列筛选
        """
        # 字段
        columns_ = []
        if "id" not in columns:
            columns_.append("id")
        columns_.extend(columns)

        # 字段字符串
        columns_str = ", ".join(columns_)
        return columns_str

    def _get_insert_sql(self):
        """
        获取新增数据的SQL
        """
        names, values = self._get_columns_str()
        sql = f"INSERT INTO {self.table} ({names}) VALUES ({values})"
        return sql

    def _to_dict(self, data: Tuple) -> Dict:
        """
        将tuple类型的结果转换为dict类型的结果
        """
        # 获取字段
        columns_ = []
        if "id" not in self.columns:
            columns_.append("id")
        columns_.extend(self.columns)

        # 转换数据
        return dict(zip(columns_, data))

    def _to_list_dict(self, data: Tuple) -> List[Dict]:
        """
        将tuple类型列表的结果转换为dict类型列表的结果
        """
        result = []
        for i in data:
            result.append(self._to_dict(i))
        return result

    async def add(self, data_dict: Dict):
        """
        添加单条数据
        """
        name_str = ", ".join(data_dict.keys())
        value_str = ", ".join(["%s" for _ in data_dict.values()])
        sql = f"INSERT INTO {self.table}({name_str}) values ({value_str})"
        await self.db.execute(sql, values=tuple(data_dict.values()))

    async def add_many(self, data: List[Dict]):
        """
        添加多条数据
        """
        if len(data) == 0:
            return

        # 准备SQL语句
        data_dict = data[0]
        name_str = ", ".join(data_dict.keys())
        value_str = ", ".join(["%s" for _ in data_dict.values()])
        sql = f"INSERT INTO {self.table}({name_str}) values ({value_str})"

        # 提取数据
        values = [tuple(item.values()) for item in data]
        sql = self._get_insert_sql()

        # 执行SQL语句
        await self.db.execute(sql, data=values)

    async def delete(self, id: int):
        """
        删除单条数据
        """
        sql = f"DELETE FROM {self.table} WHERE id = %s;"
        await self.db.execute(sql, values=[id])

    async def delete_ids(self, ids: Tuple[int]):
        """
        根据ID列表删除多条数据
        """
        ids_ = ["%s" for _ in range(len(ids))]
        ids_str = ", ".join(ids_)
        sql = f"DELETE FROM {self.table} WHERE id IN({ids_str});"
        await self.db.execute(sql, values=ids)

    async def update(self, id: int, update_dict: Dict):
        """
        更新单条数据
        """
        update_ = []
        values = []

        # 组合参数
        for k, v in update_dict.items():
            update_.append(f"{k} = %s")
            values.append(v)
        update_str = ", ".join(update_)

        # 生成SQL语句
        sql = f"UPDATE {self.table} SET {update_str} WHERE id = %s;"
        values.append(id)

        # 执行SQL语句
        await self.db.execute(sql, tuple(values))

    async def update_many(self, updates: List[Dict]):
        """
        更新多条数据
        """

        # 数组为空或者字典没有id字段，则直接返回
        if not updates or updates[0].get("id") is None:
            return

        # 更新多条数据
        for data in updates:
            # 取出ID
            id_ = data.get("id")
            del data["id"]

            update_ = []
            values = []

            # 组合参数
            for k, v in data.items():
                update_.append(f"{k} = %s")
                values.append(v)
            update_str = ", ".join(update_)

            # 生成SQL语句
            sql = f"UPDATE {self.table} SET {update_str} WHERE id = %s;"
            values.append(id_)
            await self.db.execute(sql, tuple(values))

    async def find(self, id: int) -> Tuple[Any]:
        """
        查找单条数据
        """
        # 字段字符串
        columns_str = self._get_columns_id_str(self.columns)

        # SQL语句
        sql = f"SELECT {columns_str} FROM {self.table} WHERE id = %s;"
        result = await self.db.execute(sql, values=(id,), return_all=False)

        return self._to_dict(result)

    async def find_page(self, page: int = 1, size: int = 20, order_column: str = "id", order_type: str = "DESC") -> List[Dict]:
        """
        分页查找多条数据
        """
        # 字段字符串
        columns_str = self._get_columns_id_str(self.columns)

        # 分页查询
        offset = (page - 1) * size

        # 这里采用“延迟关联”大大提高查询效率：《高性能MySQL》 第3版 242页
        sql = f"""
        SELECT {columns_str} FROM {self.table} 
        INNER JOIN(
            SELECT id FROM {self.table}
            ORDER BY id LIMIT {offset}, {size}
        ) AS t1 USING(id) 
        ORDER BY {order_column} {order_type};
        """
        result = await self.db.execute(sql)
        return self._to_list_dict(result)

    async def find_total(self) -> int:
        """
        查询数据总数
        """
        sql = f"SELECT COUNT(*) FROM {self.table};"
        result = await self.db.execute(sql)
        total = 0
        try:
            total = result[0][0]
        except:
            pass
        return total

    async def find_ids(self, ids: List[int]) -> List[Dict]:
        """
        根据ID列表查找多条数据
        """
        # 字段字符串
        columns_str = self._get_columns_id_str(self.columns)

        # 查询字符串
        query_ = ["%s" for _ in range(len(ids))]
        query_str = ", ".join(query_)

        # SQL语句
        sql = f"SELECT {columns_str} FROM {self.table} WHERE id in ({query_str});"
        result = await self.db.execute(sql, values=tuple(ids))
        return self._to_list_dict(result)
