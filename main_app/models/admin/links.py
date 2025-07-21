from mongoengine import Document, StringField, IntField, DateTimeField, ListField, DictField, EmbeddedDocument, \
    EmbeddedDocumentField, BooleanField
from datetime import datetime

class Link(Document):
    admin_uid = StringField(required=True)
    program_id = StringField()
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)
    referrer_reward_type = StringField()
    referrer_reward_value = IntField()
    referee_reward_type = StringField()
    referee_reward_value = IntField()
    reward_condition = StringField()
    success_reward = StringField()
    created_at = DateTimeField(default=datetime.now())
    active = BooleanField()
    invitation_link = StringField()

    meta = {"db_alias" : "admin-db", "collection" : "links"}

class AppStats(Document):
    admin_uid = StringField(required=True)
    program_id = StringField()
    primary_platform = StringField()
    apps = ListField(DictField())

    meta = {"db_alias": "admin-db", "collection": "SharingApps"}

class ReferralReward(Document):
    admin_uid = StringField()
    program_id = StringField()
    referrer_reward  = IntField(required=True, default=0)
    invitee_reward = IntField(required=True, default=0)
    conversion_rates = DictField()
    signup_reward = IntField(required=True, default=0)
    login_reward =IntField(required=True, default=0)
    updated_at = DateTimeField()

    meta = {"db_alias": "admin-db", "collection": "ReferralRewards"}


