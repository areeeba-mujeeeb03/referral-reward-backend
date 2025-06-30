from mongoengine import StringField, Document, DateTimeField ,FloatField, BooleanField
import datetime

class AddProduct(Document):
    uid = StringField(required=True, unique=True)
    product_name = StringField(required=True)
    original_amt = FloatField(required=True)
    image_url = StringField()
    status = StringField(default="Live")  # Options: Live, Paused
    visibility_till = DateTimeField()
    apply_offer = BooleanField()
    created_at = DateTimeField(default=datetime.datetime.now)


    meta = {"db_alias" : "admin-db", "collection" : "product"}