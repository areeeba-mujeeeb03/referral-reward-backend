from mongoengine import Document, StringField, IntField, DateTimeField

class Link(Document):
    special_link = StringField()
    created_at = DateTimeField()
    start_time = DateTimeField()
    expiry_time = DateTimeField()
    referrer_reward = IntField()
    referee_reward = IntField()

    meta = {"db_alias" : "admin-db", "collection" : "offers"}
