from mongoengine import Document, IntField, StringField


class UserData(Document):
    total_participants  = IntField()
    total_referrals = IntField()
    successful_referrals = IntField()


    meta = {"db_alias": "admin-db", "collection": "participants"}