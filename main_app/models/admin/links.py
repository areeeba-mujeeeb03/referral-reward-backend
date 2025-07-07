from mongoengine import Document, StringField, IntField, DateTimeField, ListField, DictField, EmbeddedDocument, \
    EmbeddedDocumentField
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




class AppStats(Document):
    admin_uid = StringField(required=True)
    apps = ListField(DictField())


    meta = {"db_alias": "admin-db", "collection": "SharingApps"}
