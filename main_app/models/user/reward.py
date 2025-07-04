from mongoengine import StringField, IntField, DictField, ListField, Document

class Reward(Document):
    user_id = StringField(required=True, unique=True)
    galaxy_name = ListField()
    current_planet = ListField()
    total_stars = IntField(default=0)
    total_meteors = IntField(default=200)
    redeemed_meteors = IntField(default=0)
    total_vouchers = IntField(default=0)
    discount_coupons = ListField(DictField())
    reward_history = ListField(DictField())

    meta = {"db" : "user_db", 'collection' : 'rewards'}