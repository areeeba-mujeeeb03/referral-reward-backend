from mongoengine import (StringField, Document,DictField, DateTimeField, IntField, ListField, EmbeddedDocument, EmbeddedDocumentField)
import datetime
class Offer(Document):
    admin_uid = StringField()
    program_id = StringField()
    offers = ListField(DictField())
    # offer_uid = StringField(required = True)
    # product_id = StringField()
    # offer_name = StringField(required = True)
    # one_liner = StringField(required = True)
    # image = StringField()
    # button_txt = StringField(required =True)
    # off_percent = IntField(required = True)
    # status = StringField(default="Live")  # Options: Live, Paused, Upcoming
    # start_date = DateTimeField(required = True)
    # expiry_date = DateTimeField(required = True)



    meta = {"db_alias" : "admin-db", "collection" : "offers"}



