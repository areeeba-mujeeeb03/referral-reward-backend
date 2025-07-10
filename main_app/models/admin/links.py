from mongoengine import Document, StringField, IntField, DateTimeField, ListField, DictField, EmbeddedDocument, \
    EmbeddedDocumentField, BooleanField
from datetime import datetime

class Link(Document):
    admin_uid = StringField(required=True)
    invitation_link = StringField()
    active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    start_date = DateTimeField()
    expiry_date = DateTimeField()
    referrer_reward = IntField()
    referee_reward = IntField()

    meta = {"db_alias" : "admin-db", "collection" : "links"}

class AppStats(Document):
    admin_uid = StringField(required=True)
    apps = ListField(DictField())

    meta = {"db_alias": "admin-db", "collection": "SharingApps"}

class ReferralReward(Document):
    admin_uid = StringField()
    referrer_reward  = StringField(required=True)
    referee_reward = StringField(required=True)
    conversion_rates = DictField(required=True)
    updated_on = DateTimeField()

    meta = {"db_alias": "admin-db", "collection": "ReferralRewards"}


