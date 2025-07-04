from mongoengine import Document, StringField, EmailField, DateTimeField
import datetime

class FAQ(Document):
    admin_uid = StringField(unique=True)
    faq_id = StringField(required = True)
    category = StringField()
    question = StringField(required=True)
    answer = StringField(required=True)

    meta = {"db_alias": "admin-db", "collection": "FAQs"}

    def save(self, *args, **kwargs):
        if not self.faq_id:
            self.faq_id = f"WE_FAQ_{FAQ.objects.count() + 1}"
        return super(FAQ, self).save(*args, **kwargs)

class Contact(Document):
    admin_uid = StringField(required=True, unique=True)
    user_id = StringField(required= True)
    username = StringField(required=True)
    email = EmailField(required=True)
    message = StringField(required=True)
    date = DateTimeField(default=datetime.datetime.now())

    meta = {"db_alias": "admin-db", "collection": "Messages"}