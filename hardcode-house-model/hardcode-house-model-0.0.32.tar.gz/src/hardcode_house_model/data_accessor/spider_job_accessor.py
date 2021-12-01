import logging
from datetime import datetime

from hardcode_house_model.house.spider_job import SpiderArguments, SpiderJob
from hardcode_house_model.util.bulk import BulkOperationBuilder
from hardcode_house_model.util.decorator import ExceptionLogging
from pymongo.errors import BulkWriteError

logger = logging.getLogger("hardcode_house_model.spider_job_accessor")

class SpiderJobAccessor(object):
    @classmethod
    def upsert_spider_job(cls, spider, job, spider_run_env, status, item_count, arguments):
        builder = BulkOperationBuilder()
        doc = {
            "spider": spider,
            "job": job,
            "spider_run_env": spider_run_env,
            "status": status,
            "item_count": item_count,
            "arguments": arguments,
            "updated_datetime": datetime.utcnow()
        }
        doc = {key: value for key, value in doc.items() if value is not None}
        builder.update_many(
            {
                "spider": spider,
                "job": job
            },
            {
                "$set": doc
            },
            upsert=True
        )

        with ExceptionLogging(logger, exceptions=(BulkWriteError,), rethrow=False):
            SpiderJob._get_collection().bulk_write(builder.build(), ordered=False)
