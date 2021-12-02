from datetime import date
from typing import List
from pmb_py.domain.model import Block
from pmb_py.domain.query_result import QueryResult
import pmb_py.core as core
from pmb_py.api import pmb_mixin
from pmb_py.adapter.pmb_convert import to_block

TIME_FORMAT1 = "%Y-%m-%d"


class PmbGantt:
    """對應特別為 Pmb gantt 專用的 api"""

    @classmethod
    def blcoks_between_date(cls,
                            start_date: date,
                            end_date: date,
                            project_id: int = None,
                            member_id: int = None,
                            start:int=None,
                            limit:int=None) -> QueryResult:
        """取日期間的格子

        Args:
            start_date: 起始日
            end_date: 結束日
            project_id: 專案 Id,
            member_id: 人員 pmb 編號
            start: 啟始數
            limit: 限制拿取項目數目
        
        Returns: 回傳 block 表列
        """

        data = {
            'start_date': start_date.strftime(TIME_FORMAT1),
            'end_date': end_date.strftime(TIME_FORMAT1)}
        for kw, v in {'project_id': project_id, 'member_id':member_id, 'start':start, 'limit':limit}.items():
            if v:
                data[kw] = v
        re = core._session.get('/blocks/between_date', params=data)
        if not re:
            return None

        items = re.results
        query_re = QueryResult(
            limit=re.limit, next=re.next, previous=re.previous, results=list(), start=re.start, total_count=re.total_count)
        objects = [to_block(item) for item in items]
        query_re.results = {object.id: object for object in objects}.values()
        return query_re
