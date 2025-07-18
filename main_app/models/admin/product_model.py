from mongoengine import StringField, Document, ListField, DictField,FloatField, BooleanField, EmbeddedDocument, EmbeddedDocumentField
import datetime

class Product(Document):
    admin_uid = StringField(required=True, unique=True)
    products = ListField(DictField())
    # product_name = StringField(required=True)
    # original_amt = FloatField(required=True)
    # short_desc = StringField(required=True)
    # image = StringField()
    # reward_type = StringField()
    # admin_uid = StringField(required=True)

    meta = {"db_alias" : "admin-db", "collection" : "product"}


# class Product(EmbeddedDocument):
#     product_id = StringField(required=True, unique=True)
#     product_name = StringField()
#     original_amt = FloatField(required=True)
#     short_desc = StringField(required=True)
#     image = StringField()
#     reward_type = StringField()

# class ProductList(Document):
#     admin_uid = StringField(required=True)
#     products = ListField(EmbeddedDocumentField(Product))

#     meta = {"db_alias" : "admin-db", "collection" : "product"}

















    # discounted_amt = FloatField(required=True)
    # status = StringField(default="Live")  # Options: Live, Paused
    # visibility_till = DateTimeField()
    # apply_offer = BooleanField()

    #  # Offer-related fields
    # offer_name = StringField()
    # one_liner = StringField()
    # button_txt = StringField()
    # off_percent = FloatField()
    # start_date = DateTimeField()
    # expiry_date = DateTimeField()
    # offer_type = StringField()
    # offer_status = StringField()
    # voucher_code = StringField()
    # created_at = DateTimeField(default=datetime.datetime.now)
