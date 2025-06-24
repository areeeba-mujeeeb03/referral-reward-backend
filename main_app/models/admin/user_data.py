from mongoengine import StringField, IntField, Document

class UserData(Document):
    total_participants  = IntField()
    total_referrals = IntField()
    succeccful_referrals = IntField()

    meta = {"collection" : ""}
