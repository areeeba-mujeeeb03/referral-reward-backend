from mongoengine import Document, IntField, StringField

class Participants(Document):
    admin_uid = StringField(required=True,unique=True)
    program_id = StringField()
    total_participants  = IntField(default=0)
    total_referrals = IntField(default=0)
    successful_referrals = IntField(default=0)
    referral_leads = IntField(default=0)
    referral_earnings = IntField(default=0)
    game_earnings = IntField(default=0)
    purchases_earnings = IntField(default=0)
    milestones_earnings = IntField(default=0)
    signup_earnings = IntField(default=0)
    vouchers_won = IntField(default=0)
    used_coupons = IntField(default=0)
    currencies_converted = IntField(default=0)

    meta = {"db_alias": "admin-db", "collection": "participants"}