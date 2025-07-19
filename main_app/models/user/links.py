from mongoengine import DateTimeField, StringField, IntField,Document

class Link(Document):
    user_id = StringField(required=True, unique=True)
    verification_code = IntField()
    expiry = DateTimeField()
    sent_at  = DateTimeField()
    changed_on = DateTimeField()
    expiry_time = DateTimeField()
    otp = IntField()
    otp_expires_at = DateTimeField()
    otp_requested_at = DateTimeField()
    link_expiry_time = IntField()
    generation_time = IntField()

    meta = {"db" : "user-db" ,"collection" : "links"}