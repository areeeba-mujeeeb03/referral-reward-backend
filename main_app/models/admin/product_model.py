from mongoengine import StringField, Document, ListField, DictField,FloatField, BooleanField, EmbeddedDocument, EmbeddedDocumentField
import datetime

class Product(Document):
    admin_uid = StringField(required=True)
    program_id = StringField()
    products = ListField(DictField())
    # product_name = StringField(required=True)
    # original_amt = FloatField(required=True)
    # short_desc = StringField(required=True)
    # image = StringField()
    # reward_type = StringField()
    # admin_uid = StringField(required=True)

    meta = {"db_alias" : "admin-db", "collection" : "product"}
