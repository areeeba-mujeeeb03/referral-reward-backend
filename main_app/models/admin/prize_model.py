from mongoengine import Document, StringField, DateTimeField
import datetime

class ExcitingPrize(Document):
    title = StringField(required = True)
    image_url = StringField()
    terms_conditions = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias" : "admin-db", "collection" : "prizes"}