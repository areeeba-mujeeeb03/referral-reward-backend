from mongoengine import (StringField, Document, DateTimeField, IntField, ListField, EmbeddedDocument, EmbeddedDocumentField)
import datetime
# class Offer(EmbeddedDocument):
#     offer_uid = StringField(required = True, Unique = True)
#     product_id = StringField()
#     # admin_uid = StringField()
#     offer_name = StringField(required = True)
#     one_liner = StringField(required = True)
#     image = StringField()
#     button_txt = StringField(required =True)
#     off_percent = IntField(required = True)
#     status = StringField(default="Live")  # Options: Live, Paused, Upcoming
#     start_date = DateTimeField()
#     expiry_date = DateTimeField()

# class OfferSection(Document):
#     admin_uid = StringField(required=True)
#     offer = ListField(EmbeddedDocumentField(Offer)) 



class Offer(Document):
    offer_uid = StringField(required = True)
    product_id = StringField()
    admin_uid = StringField()
    offer_name = StringField(required = True)
    one_liner = StringField(required = True)
    image = StringField()
    button_txt = StringField(required =True)
    off_percent = IntField(required = True)
    status = StringField(default="Live")  # Options: Live, Paused, Upcoming
    start_date = DateTimeField(required = True)
    expiry_date = DateTimeField(required = True)



    meta = {"db_alias" : "admin-db", "collection" : "offers"}



