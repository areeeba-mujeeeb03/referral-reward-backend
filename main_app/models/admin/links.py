from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime

class Link(Document):
    admin_uid = StringField(required=True, unique=True)
    invitation_link = StringField()
    created_at = DateTimeField(default=datetime.now)
    start_date = DateTimeField()
    expiry_date = DateTimeField()
    referrer_reward = IntField()
    referee_reward = IntField()

    meta = {"db_alias" : "admin-db", "collection" : "links"}


class LinkSharing(Document):
    admin_uid = StringField(required=True, unique=True)
    app_name = StringField()
    total_sent = IntField(default=0)
    successful_registered = IntField(required=True,default = 0)

    meta = {"db_alias": "admin-db", "collection": "SharingApps"}
