from mongoengine import StringField, IntField, EmailField, Document, DateTimeField, BooleanField
from main_app.utils.user.helpers import generate_tag_id, generate_invite_link

class User(Document):
    admin_uid = StringField()
    program_id = StringField(required=True)
    tag_id = StringField(required=True)
    user_id = StringField(required=True)
    name = StringField(required=True)
    email = EmailField(required=True)
    mobile_number = StringField(required=True)
    password = StringField(required=True)
    invitation_link = StringField()
    invitation_code = StringField()
    access_token = StringField()
    session_id = StringField()
    referred_by = StringField(default=None)
    joining_status = StringField(default="pending")
    created_at = DateTimeField()
    login_count = IntField()
    profile_picture = StringField()
    is_member = BooleanField(default= False)
    joined_via = StringField(defaul = None)
    expiry_time = DateTimeField()
    otp = IntField()
    otp_expires_at = DateTimeField()
    otp_requested_at = DateTimeField()
    link_expiry_time = IntField()
    generation_time = IntField()

    meta = {"db" : "user-db", 'collection': 'users'}

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = f"WE_UID_{User.objects.count() + 1}"
        if not self.tag_id:
            self.tag_id = generate_tag_id(self.name, self.mobile_number)
        if not self.invitation_link:
            self.invitation_link = generate_invite_link(self.tag_id)
        if not self.invitation_code:
            self.invitation_code = f"WECODE{User.objects.count() + 1}"
        return super(User, self).save(*args, **kwargs)