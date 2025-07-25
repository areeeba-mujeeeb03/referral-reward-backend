from mongoengine import Document, StringField, EmailField, DateTimeField, EmbeddedDocument, DictField, ListField, \
    EmbeddedDocumentField
import datetime

# class FAQ(Document):
#     admin_uid = StringField(unique=True)
#     faq_id = StringField(required = True)
#     category = StringField()
#     question = StringField(required=True)
#     answer = StringField(required=True)
#
#     meta = {"db_alias": "admin-db", "collection": "FAQs"}
#
#     def save(self, *args, **kwargs):
#         if not self.faq_id:
#             self.faq_id = f"WE_FAQ_{FAQ.objects.count() + 1}"
#         return super(FAQ, self).save(*args, **kwargs)

class FAQ(Document):
    admin_uid = StringField(required=True, unique=True)
    categories = ListField(DictField(), default=list)
    meta = {"db_alias": "admin-db", "collection": "FAQs"}

class Contact(Document):
    admin_uid = StringField(required=True)
    program_id = StringField()
    user_id = StringField(required= True)
    name = StringField(required=True)
    email = EmailField(required=True)
    message = StringField(required=True)
    file_url = ListField(StringField())

    date = DateTimeField(default=datetime.datetime.now())

    meta = {"db_alias": "admin-db", "collection": "Messages"}