from mongoengine import Document, IntField, DateTimeField
from datetime import datetime

class dashboard_data(Document):
    total_participants = IntField()
    referral_leads = IntField()
    successful_referrals = IntField()
    total_referrals = IntField()
    converted_referrals = IntField()
    total_used_coupons = IntField()
    total_rewards_given = IntField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'dashboard_data'
    }
