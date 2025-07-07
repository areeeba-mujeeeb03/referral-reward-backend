from mongoengine import StringField, IntField, DictField, ListField, Document


class Referral(Document):
    user_id = StringField(required=True, unique=True)
    total_referrals = IntField(default=0)
    referral_earning = IntField(default=0)
    pending_referrals = IntField(default=0)
    successful_referrals = IntField(default=0)
    all_referrals = ListField(DictField())

    meta = {"db" : "user-db", 'collection': 'referrals'}