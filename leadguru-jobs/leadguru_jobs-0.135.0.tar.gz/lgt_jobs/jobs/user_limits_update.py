from abc import ABC
from datetime import datetime
from typing import Optional, List

from cachetools import cached, TTLCache
from lgt_data.engine import UserCreditStatementDocument
from lgt_data.enums import UserAccountState
from lgt_data.model import UserModel
from lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository, \
    to_object_id
from pydantic import BaseModel

from .analytics import TrackAnalyticsJobData, TrackAnalyticsJob
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob
from ..runner import BackgroundJobRunner

"""
User limits handling
"""

class UpdateUserDataUsageJobData(BaseBackgroundJobData, BaseModel):
    channel_id: Optional[str]
    bot_name: Optional[str]
    dedicated_bot_id: Optional[str]
    filtered: bool
    message: Optional[str]

class UpdateUserDataUsageJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return UpdateUserDataUsageJobData

    @staticmethod
    def increment(user_id: str, filtered: bool, dedicated_bot_id: str = None, bot_name: str = None):
        message = TrackAnalyticsJobData(**{
            "event": 'user-message-processed',
            "data": str(user_id),
            "name": "1" if filtered else "0",
            "created_at": datetime.utcnow(),
            "extra_id": dedicated_bot_id,
            "attributes": [
                str(user_id),
                "1" if filtered else "0",
            ]
        })
        BackgroundJobRunner.submit(TrackAnalyticsJob, message)

        print(f"[UpdateUserDataUsageJob] Updating user: {user_id}")
        UserCreditStatementDocument(
            user_id=to_object_id(user_id),
            created_at=datetime.utcnow(),
            balance=-1,
            action="lead-filtered",
            attributes=[bot_name if bot_name else "", dedicated_bot_id if dedicated_bot_id else ""]
        ).save()

    @staticmethod
    @cached(cache=TTLCache(maxsize=500, ttl=600))
    def get_users() -> List[UserModel]:
        return UserMongoRepository().get_users()

    def exec(self, data: UpdateUserDataUsageJobData):
        if data.dedicated_bot_id:
            bot = DedicatedBotRepository().get_by_id(data.dedicated_bot_id)
            if not bot:
                return

            user = UserMongoRepository().get(bot.user_id)
            if user.leads_limit < user.leads_proceeded:
                return

            self.increment(bot.user_id, data.filtered, data.dedicated_bot_id)
            return

        users = self.get_users()
        for user in users:
            if user.state == UserAccountState.Suspended.value:
                continue

            if user and data.bot_name in user.excluded_workspaces:
                continue

            if user and user.excluded_channels and user.excluded_channels.get(data.bot_name) and \
                    (data.channel_id in user.excluded_channels.get(data.bot_name)):
                continue

            self.increment(f"{user.id}", data.filtered, data.bot_name)
