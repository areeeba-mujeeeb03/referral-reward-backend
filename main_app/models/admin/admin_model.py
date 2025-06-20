from mongoengine import StringField, Document, EmailField, DateTimeField
import datetime

class User(Document):
    admin_uid = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    access_token = StringField()
    session_id = StringField()
    expiry_time = DateTimeField()

    meta = {'collection': 'admin'}

    def save(self, *args, **kwargs):
        if not self.admin_uid:
            self.admin_uid = f"AD_UID_{User.objects.count() + 1}"
        return super(User, self).save(*args, **kwargs)

