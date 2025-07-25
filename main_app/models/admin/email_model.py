# from mongoengine import Document, StringField, FileField, EmailField

# class EmailTemplate(Document):
#     admin_uid = StringField(required=True)
#     email_type = StringField(required=True, choices=["milestone", "referral", "promotional"])
#     name = StringField()
#     email = StringField()
#     subject = StringField()
#     reply_to = EmailField()
#     content = StringField()
#     button_text = StringField()
#     button_url = StringField()
#     image_type = StringField(choices=["header", "logo"])
#     image_path = StringField() 

#     meta = {"db_alias" : "admin-db", "collection" : "emails"}



from mongoengine import Document, EmbeddedDocument, StringField, EmailField, EmbeddedDocumentField, DictField

class EmailData(EmbeddedDocument):
    name = StringField()
    email = StringField()
    subject = StringField()
    reply_to = EmailField()
    content = StringField()
    button_text = StringField()
    button_url = StringField()
    image_type = StringField(choices=["header", "logo"])
    image_path = StringField()

class EmailTemplate(Document):
    admin_uid = StringField(required=True)
    all_emails = DictField(field=EmbeddedDocumentField(EmailData))  # key = email_type

    meta = {"db_alias": "admin-db", "collection": "emails"}

