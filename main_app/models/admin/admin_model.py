from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField


class Admin(Document):
    admin_uid = StringField(required=True)
    username = StringField(required=True)
    email = EmailField(required=True)
    mobile_number = StringField(required = True)
    password = StringField(required=True)
    access_token = StringField()
    session_id = StringField()
    expiry_time = DateTimeField()
    profile_picture = StringField()
    # OTP Fields
    code = StringField()
    code_expiry = DateTimeField()
    all_campaigns = ListField(DictField())

    meta = {"db_alias" : "admin-db", 'collection': 'admin'}

    def save(self, *args, **kwargs):
        if not self.admin_uid:
            self.admin_uid = f"AD_UID_{Admin.objects.count() + 1}"
        return super(Admin, self).save(*args, **kwargs)

