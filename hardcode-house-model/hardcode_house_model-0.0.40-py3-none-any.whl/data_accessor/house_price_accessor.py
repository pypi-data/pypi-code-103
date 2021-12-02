import logging
from datetime import datetime

from elasticsearch.exceptions import ConnectionTimeout
from hardcode_house_model.house.house_deal import HouseDeal
from hardcode_house_model.house.house_price import (HousePrice,
                                                    HousePriceHistory)
from hardcode_house_model.util.bulk import BulkOperationBuilder
from hardcode_house_model.util.decorator import ExceptionLogging
from mongo_driver.errors import BulkOperationError
from retry import retry

logger = logging.getLogger("hardcode_house_model.house_price_accessor")

class HousePriceAccessor(object):

    @classmethod
    def get_house_price_history_count(cls, job):
        return HousePriceHistory.count({"scrapy_job": job})

    @classmethod
    def upsert_house_price(cls, spider, job, items):
        with ExceptionLogging(logger, swallow_exceptions=(BulkOperationError,)):
            with HousePrice.bulk(unordered=True) as bulk_context:
                for item in items:
                    if "_type" in item:
                        del item["_type"]
                    doc = item
                    doc["updated_datetime"] = datetime.utcnow()
                    HousePrice.bulk_update(
                        bulk_context,
                        {
                            "platform": item["platform"],
                            "platform_house_id": item["platform_house_id"],
                            "scrape_datetime": {
                                "$lte": doc["scrape_datetime"]
                            }
                        },
                        {
                            "$set": doc
                        },
                        upsert=True
                    )

    @classmethod
    def upsert_house_price_history(cls, spider, job, items):
        with ExceptionLogging(logger, swallow_exceptions=(BulkOperationError,)):
            with HousePriceHistory.bulk(unordered=True) as bulk_context:
                for item in items:
                    calendar = item["scrape_datetime"].isocalendar()
                    doc = {
                        "platform": item["platform"],
                        "platform_house_id": item["platform_house_id"],
                        "snapshot_date": item["scrape_datetime"],
                        "scrapy_job": job,
                        "calendar_year": calendar[0],
                        "calendar_weeknumber": calendar[1],
                        "calendar_weekday": calendar[2],
                        "quotation": {
                            "total_price": item["total_price"],
                            "unit_price": item["unit_price"],
                        },
                        "location": item["location"],
                        "area": item["area"],
                        "estate_name": item["estate_name"],
                        "updated_datetime": datetime.utcnow(),
                    }
                    HousePriceHistory.bulk_update(
                        bulk_context,
                        {
                            "platform": item["platform"],
                            "platform_house_id": item["platform_house_id"],
                            "snapshot_date": item["scrape_datetime"]
                        },
                        {
                            "$set": doc
                        },
                        upsert=True
                    )