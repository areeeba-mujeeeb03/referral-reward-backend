from mongoengine import Document, IntField, StringField

class UserData(Document):
    admin_uid = StringField(required=True,unique=True)
    total_participants  = IntField()
    total_referrals = IntField()
    successful_referrals = IntField()
    referral_leads = IntField()
    referral_earnings = IntField()
    game_earnings = IntField()
    purchases_earnings = IntField()
    milestones_earnings = IntField()
    signup_earnings = IntField()
    currencies_converted = IntField()

    meta = {"db_alias": "admin-db", "collection": "participants"}