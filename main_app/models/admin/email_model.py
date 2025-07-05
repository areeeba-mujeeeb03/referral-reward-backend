from mongoengine import Document, StringField, FileField, EmailField

class EmailTemplate(Document):
    email_type = StringField(required=True, choices=["milestone", "referral", "promotional"])
    name = StringField()
    email = StringField()
    subject = StringField()
    reply_to = EmailField()
    content = StringField()
    button_text = StringField()
    button_url = StringField()
    image_type = StringField(choices=["header", "logo"])
    image_path = StringField()  # store path or URL
