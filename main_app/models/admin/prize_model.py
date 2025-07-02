from mongoengine import Document, StringField, DateTimeField, IntField
import datetime

class ExcitingPrize(Document):
    admin_uid = StringField( unique=True)
    title = StringField(required = True)
    image_url = StringField()
    term_conditions = StringField()
    required_meteors = IntField(required=True, default=0)
    # usmeteors = IntField(required=True, default=0)
    created_at = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias" : "admin-db", "collection" : "prizes"}