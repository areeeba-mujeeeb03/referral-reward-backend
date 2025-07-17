from mongoengine import Document, StringField, DateTimeField, ListField, EmbeddedDocumentField, IntField, \
    EmbeddedDocument, BooleanField


class SpecialOffer(EmbeddedDocument):
    offer_title = StringField()
    offer_desc  =StringField()
    tag = StringField()
    start_date = DateTimeField()
    start_time =DateTimeField()
    end_date =DateTimeField()
    end_time = DateTimeField()
    offer_code = StringField()
    pop_up_text = StringField()
    start_timestamp = DateTimeField()
    expiry_timestamp = DateTimeField()
    active = BooleanField()

class Offer(Document):
    admin_uid = StringField()
    special_offer = ListField(EmbeddedDocumentField(SpecialOffer))

    meta = {"db_alias" : "admin-db", "collection" : "SpecialOffer"}
