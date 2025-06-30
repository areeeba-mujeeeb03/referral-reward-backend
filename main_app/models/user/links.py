from mongoengine import DateTimeField, StringField, IntField,Document

class Link(Document):
    user_id = StringField()
    token = StringField()
    expiry = DateTimeField()
    sent_at  = DateTimeField()
    changed_on = DateTimeField()

    meta = {"db" : "user-db" ,"collection" : "links"}