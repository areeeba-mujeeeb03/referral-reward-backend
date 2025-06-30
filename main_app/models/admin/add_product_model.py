from mongoengine import StringField, Document, DateTimeField, FloatField, BooleanField, ImageField
import datetime

class Product(Document):
    uid = StringField(required=True, unique=True)
    product_name = StringField(required=True)
    original_amt = FloatField(required=True)
    discounted_amt = FloatField(required = True)
    image_url = ImageField()
    reward_type = StringField()
    short_desc = StringField()
    status = StringField(default="Live")
    visibility_till = DateTimeField()
    apply_offer = BooleanField()
    created_at = DateTimeField(default=datetime.datetime.now)


    meta = {"db_alias" : "admin-db", "collection" : "product"}