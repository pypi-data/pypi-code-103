import sys
from pathlib import Path
import os

base_dir = (Path(__file__).resolve()).parent

from lrabbit_scrapy import BaseSpider
import sqlalchemy as sa
from lrabbit_scrapy.utils import get_html_by_url, get_css_selector_by_url
from parsel import Selector
import random


class Spider(BaseSpider):
    # setup
    is_open_mysql = False
    is_drop_tables = False
    reset_task_list = True

    # datastore
    table_table1 = [
        sa.Column('val', sa.String(255)),
        sa.Column('val2', sa.String(255))
    ]

    file_blogPost = [
        'id', 'title', 'datetime', 'content'
    ]

    def __init__(self, spider_name):
        super(Spider, self).__init__(spider_name)

    async def worker(self, task):
        """

        code your worker method

        :param task:
        :return:
        """
        # await self.insert_one(self.tables['table1'].insert().values(val=str(task)))
        # await self.insert_one(self.tables['table2'].insert().values(val=str(task)))
        # res = await self.query(self.tables['table1'].select())
        # res = await res.fetchall()

        url = f"http://www.lrabbit.life/post_detai/?id={task}"
        selector = await get_css_selector_by_url(url)
        title = selector.css(".detail-title h1::text").get()
        datetime = selector.css(".detail-info span::text").get()
        content = ''.join(selector.css(".detail-content *::text").getall())
        data = {"id": task, 'title': title, 'datetime': datetime, 'content': content}
        if title:
            self.all_files['blogPost'].write(data)

    async def create_tasks(self):
        return [i for i in range(100)]


if __name__ == '__main__':
    s = Spider(__file__)
    s.run()
