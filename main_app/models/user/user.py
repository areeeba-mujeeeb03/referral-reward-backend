from mongoengine import StringField, IntField, EmailField, Document, DateTimeField, BooleanField
from main_app.utils.user.helpers import generate_tag_id, generate_invite_link

class User(Document):
    user_id = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    mobile_number = StringField(required=True, unique=True)
    password = StringField(required=True)
    tag_id = StringField()
    invitation_link = StringField()
    invitation_code = StringField()
    access_token = StringField()
    session_id = StringField()
    referred_by = StringField(default=None)
    joining_status = StringField(default="pending")
    created_at = DateTimeField()
    is_active = BooleanField()
    expiry_time = DateTimeField()
    otp = IntField()
    expires_at = DateTimeField()
    login_count = IntField()
    generation_time = IntField()
    link_expiry_time = IntField()
    is_member = BooleanField(default= False)

    meta = {"db" : "user-db", 'collection': 'users'}

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = f"WE_UID_{User.objects.count() + 1}"
        if not self.tag_id:
            self.tag_id = generate_tag_id(self.username, self.mobile_number)
        if not self.invitation_link:
            self.invitation_link = generate_invite_link(self.user_id)
        if not self.invitation_code:
            self.invitation_code = f"WECODE{User.objects.count() + 1}"
        return super(User, self).save(*args, **kwargs)