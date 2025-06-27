from mongoengine import StringField, Document, DateTimeField ,FloatField
import datetime

class AddProduct(Document):
    uid = StringField(required=True, unique=True)
    product_name = StringField(required=True)
    original_amt = FloatField(required=True)
    image_url = StringField()
    status = StringField(default="Live")  # Options: Live, Paused
    visibility_till = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)


    meta = {"db_alias" : "admin-db", "collection" : "product"}