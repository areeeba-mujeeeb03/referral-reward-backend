from mongoengine import StringField, IntField, DictField, ListField, Document

class Reward(Document):
    user_id = StringField(required=True, unique=True)
    galaxy_name = ListField()
    current_planet = ListField()
    total_meteors_earned = IntField(default=0)
    total_stars = IntField(default=0)
    total_currency = IntField(default=0)
    current_meteors = IntField(default=0)
    redeemed_meteors = IntField(default=0)
    total_vouchers = IntField(default=0)
    used_vouchers = IntField(default=0)
    unused_vouchers = IntField(default=0)
    discount_coupons = ListField(DictField())
    reward_history = ListField(DictField())
    redeem_history = ListField(DictField())
    product_history = ListField(DictField())

    meta = {"db" : "user_db", 'collection' : 'rewards'}