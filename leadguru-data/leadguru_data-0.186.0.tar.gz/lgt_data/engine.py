import os
from datetime import datetime
from typing import Dict, Tuple

from mongoengine import connect, Document, DateTimeField, StringField, IntField, ObjectIdField, ListField

connect(host=os.environ.get('MONGO_CONNECTION_STRING', 'mongodb://127.0.0.1:27017/'), db="lgt_admin", alias="lgt_admin")
connect(host=os.environ.get('MONGO_CONNECTION_STRING', 'mongodb://127.0.0.1:27017/'), db="lgt_leads", alias="lgt_leads")

class UserTrackAction(Document):
    user_id = ObjectIdField(required=True)
    action = StringField(required=True)
    metadata = StringField(required=False)
    created_at = DateTimeField(required=True)
    meta = { "indexes": ["user_id"], "db_alias": "lgt_admin" }

    @staticmethod
    def get_aggregated() -> Dict[str, Tuple[datetime, datetime]]:
        pipeline = [
            {
                "$group": {
                    "_id": "$user_id",
                    "last_action_at": {"$max": "$created_at"},
                    "first_action_at": {"$min": "$created_at"}
                }
            }]


        result = list(UserTrackAction.objects.aggregate(*pipeline))

        return {str(item.get("_id")):(item["first_action_at"], item["last_action_at"]) for item in result}



class DelayedJob(Document):
    created_at = DateTimeField(required=True)
    scheduled_at = DateTimeField(required=True)
    job_type = StringField(required=True)
    data = StringField(required=True)
    jib = StringField(required=True)
    executed_at: DateTimeField(required=False)

    meta = { "indexes": ["-scheduled_at", "jib"], "db_alias": "lgt_leads" }

class UserCreditStatementDocument(Document):
    meta = {"indexes": [("user_id", "created_at"),
                        ("user_id", "created_at", "action")], "db_alias": "lgt_leads"}

    user_id = ObjectIdField(required=True)
    created_at = DateTimeField(required=True)
    balance = IntField(required=True)
    action = StringField(required=True)
    lead_id = StringField(required=False)
    attributes = ListField(field=StringField(),required=False)

class UserFeedLead(Document):
    meta = {"indexes": ["user_id", "created_at", ("user_id", "created_at")],
            "db_alias": "lgt_leads"}
    user_id = ObjectIdField(required=True)
    lead_id = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(required=True)
    full_message_text = StringField(required=True)


