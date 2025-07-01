from mongoengine import StringField, Document, DateTimeField, IntField
import datetime
class Offer(Document):
    offer_uid = StringField(required = True, unique = True)
    offer_name = StringField(required = True, unique = True)
    one_liner = StringField(required = True, unique =True)
    image_url = StringField()
    button_txt = StringField(required =True)
    off_percent = IntField(required = True)
    start_date = DateTimeField(required = True)
    expiry_date = DateTimeField(required = True)


    meta = {"db_alias" : "admin-db", "collection" : "offers"}



