from mongoengine import StringField, Document, DateTimeField ,FloatField, BooleanField
import datetime

class Product(Document):
    uid = StringField(required=True, unique=True)
    product_name = StringField(required=True)
    original_amt = FloatField(required=True)
    discounted_amt = FloatField(required=True)
    short_desc = StringField(required=True)
    image_url = StringField()
    reward_type = StringField()
    status = StringField(default="Live")  # Options: Live, Paused
    visibility_till = DateTimeField()
    apply_offer = BooleanField()

     # Offer-related fields
    offer_name = StringField()
    one_liner = StringField()
    button_txt = StringField()
    off_percent = FloatField()
    start_date = DateTimeField()
    expiry_date = DateTimeField()

    created_at = DateTimeField(default=datetime.datetime.now)



    meta = {"db_alias" : "admin-db", "collection" : "product"}