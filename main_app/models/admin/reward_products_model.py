from mongoengine import StringField, Document, EmailField, DateTimeField, IntField
import datetime

class Products(Document):
    product_name = StringField(required = True, Unique = True)
    offer_description = StringField(default=0)
    off_percent = IntField(required = True)
    start_date = DateTimeField(required = True)
    expiry_date = DateTimeField(required = True)

<<<<<<< HEAD
    meta = {"db_alias" : "admin-db", "collection" : "offers"}
=======
    meta = {"db_alias" : "admin-db", "collection" : "offers"}



>>>>>>> 16e33ae1762c16826d81f55eaaffff57d8b569c0
