from typing import Dict, List
from zdpapi_mysql import Mysql, Crud
from zdpapi.libs.fastapi import APIRouter
from .response import response_bool, response_bool_data
from .request_schema import IdsSchema
from .response_schema import ResponseBool, ResponseBoolData, ResponseBoolListData
# mysql 默认配置
default_mysql_config = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'test'
}


class CRUDRouter:
    def __init__(self,
                 table_name: str,  # 必填
                 columns: List[str],  # 必填
                 schema,  # 必填
                 chinese_name: str = None,
                 tags: List[str] = None,
                 mysql_config: Dict = default_mysql_config,
                 ) -> None:

        self.db = Mysql(**mysql_config)
        self.table = table_name
        self.crud = Crud(self.db, table_name, columns)
        self.router = APIRouter()
        self.schema = schema
        self.chinese_name = chinese_name
        if self.chinese_name is None:
            self.chinese_name = table_name
        self.tags = tags
        if self.tags is None:
            self.tags = [f"{self.chinese_name}管理"]

    def register(self, app):
        """
        注册路由到APP
        """
        self.add(self.router)
        self.add_many(self.router)
        self.delete(self.router)
        self.delete_ids(self.router)
        self.update(self.router)
        self.update_many(self.router)
        self.find_one(self.router)
        self.find_ids(self.router)
        self.find_page(self.router)
        app.include_router(self.router)
        return app

    def add(self, router):
        """
        添加路由
        """
        # @self.post(path, tags=tags, summary=f"新增单条{model_.__cname__}数据")
        @router.post(f"/{self.table}", tags=self.tags, summary=f"新增单条{self.chinese_name}数据")
        async def add_router(schema: self.schema):
            await self.crud.add(schema.dict())
            return response_bool

    def add_many(self, router):
        """
        添加多条数据的路由
        """
        @router.post(f"/{self.table}s", tags=self.tags, summary=f"新增多条{self.chinese_name}数据")
        async def add_many_router(data: List[self.schema]):
            data = [item.dict() for item in data]
            await self.crud.add_many(data)
            return response_bool

    def delete(self, router):
        """
        根据ID删除数据的路由
        """
        @router.delete(f"/{self.table}/"+"{id}", tags=self.tags, summary=f"删除单条{self.chinese_name}数据")
        async def delete(id: int):
            # 根据ID删除数据
            await self.crud.delete(id)
            return response_bool

    def delete_ids(self, router):
        """
        根据ID列表删除数据的路由
        """
        @router.delete(f"/{self.table}s", tags=self.tags, summary=f"删除多条{self.chinese_name}数据")
        async def delete_ids(ids: IdsSchema):
            # 根据ID列表删除数据
            await self.crud.delete_ids(tuple(ids.ids))
            return response_bool

    def update(self, router):
        """
        根据ID更新数据的路由
        """
        @router.put(f"/{self.table}/"+"{id}", tags=self.tags, summary=f"更新单条{self.chinese_name}数据")
        async def update(id: int, data: self.schema):
            data_ = data.dict()
            if data_.get("id") is not None:
                del data_["id"]
            await self.crud.update(id, data_)
            return response_bool

    def update_many(self, router):
        """
        根据ID批量更新数据的路由
        """
        @router.put(f"/{self.table}s", tags=self.tags, summary=f"更新多条{self.chinese_name}数据")
        async def update_many(data: List[self.schema]):
            data_ = [item.dict() for item in data]
            await self.crud.update_many(data_)
            return response_bool

    def find_one(self, router):
        """
        根据ID查询单条数据
        """
        @router.get(f"/{self.table}/"+"{id}", tags=self.tags, summary=f"查找单条{self.chinese_name}数据")
        async def find_one(id: int):
            result = await self.crud.find(id)
            response = ResponseBoolData()
            response.data = result
            return response

    def find_ids(self, router):
        """
        根据ID列表查询多条数据
        """
        @router.put(f"/{self.table}_ids", tags=self.tags, summary=f"查找多条{self.chinese_name}数据")
        async def find_ids(ids: IdsSchema):
            result = await self.crud.find_ids(ids.ids)
            response = ResponseBoolListData()
            response.data = result
            return response

    def find_page(self, router):
        """
        根据ID列表查询多条数据
        """
        @router.get(f"/{self.table}s", tags=self.tags, summary=f"分页查找多条{self.chinese_name}数据")
        async def find_page(page: int = 1, size: int = 20, order_column: str = "-id"):
            # 排序方式 id正序 -id逆序
            order_type: str = "ASC"
            if order_column.startswith("-"):
                order_type = "DESC"
                order_column = order_column[1:]  # 移除“-”号

            response = ResponseBoolListData()

            # 查询总数
            total = await self.crud.find_total()
            if total == 0:  # 没有数据，没必要继续查找，浪费性能
                return response
            response.total = total

            # 分页查询
            result = await self.crud.find_page(page, size, order_column, order_type)
            response.data = result
            return response
