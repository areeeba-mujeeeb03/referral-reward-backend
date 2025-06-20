from mongoengine import StringField, IntField, DictField, ListField, Document

class Reward(Document):
    user_id = StringField(required=True, unique=True)
    galaxy_name = StringField(default="Milky Way Galaxy")
    current_planet = StringField(default= "planet A")
    total_stars = IntField(default=0)
    total_meteors = IntField(default=200)
    total_vouchers = IntField(default=0)
    discount_coupons = ListField(DictField())
    reward_history = ListField(DictField())

    meta = {'collection' : 'rewards'}