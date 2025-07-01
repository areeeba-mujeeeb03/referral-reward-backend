from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime

class Link(Document):
    invitation_link = StringField()
    created_at = DateTimeField(default=datetime.now)
    start_date = DateTimeField()
    expiry_date = DateTimeField()
    referrer_reward = IntField()
    referee_reward = IntField()

    meta = {"db_alias" : "admin-db", "collection" : "links"}


class LinkSharing(Document):
    facebook_sent = IntField()
    whatsapp_sent = IntField()
    telegram_sent = IntField()
    twitter_sent = IntField()

    meta = {"db_alias": "admin-db", "collection": "SharingApps"}
