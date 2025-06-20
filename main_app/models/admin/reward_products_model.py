from mongoengine import StringField, Document, EmailField, DateTimeField, IntField
import datetime

class Products(Document):
    product_name = StringField(required = True, Unique = True)
    offer_description = StringField(default=0)
    off_percent = IntField(required = True)
    start_date = DateTimeField(required = True)
    expiry_date = DateTimeField(required = True)

    meta = {"collection" : "offers"}