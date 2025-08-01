from mongoengine import StringField, IntField, DictField, ListField, Document, EmbeddedDocumentField, EmbeddedDocument

class Milestone(EmbeddedDocument):
    milestone_name = StringField()
    milestone_status = StringField()

class Galaxy(EmbeddedDocument):
    galaxy_name = StringField()
    milestones = ListField(EmbeddedDocumentField(Milestone))


class Reward(Document):
    user_id = StringField(required=True, unique=True)
    galaxies = ListField(EmbeddedDocumentField(Galaxy))
    # galaxy_name = ListField(DictField())
    # current_planet = ListField(DictField())
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