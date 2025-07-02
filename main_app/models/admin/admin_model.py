from mongoengine import StringField, Document, EmailField, DateTimeField

class Admin(Document):
    admin_uid = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    mobile_number = StringField(required = True, unique = True)
    password = StringField(required=True)
    access_token = StringField()
    session_id = StringField()
    expiry_time = DateTimeField()
    # OTP Fields
    code = StringField()
    code_expiry = DateTimeField()


    meta = {"db_alias" : "admin-db", 'collection': 'admin'}

    def save(self, *args, **kwargs):
        if not self.admin_uid:
            self.admin_uid = f"AD_UID_{Admin.objects.count() + 1}"
        return super(Admin, self).save(*args, **kwargs)

