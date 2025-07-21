# from mongoengine import Document, StringField, DateTimeField, IntField
# import datetime

# class ExcitingPrize(Document):
#     admin_uid = StringField( unique=True)
#     title = StringField(required = True)
#     image_url = StringField()
#     term_conditions = StringField()
#     required_meteors = IntField(required=True, default=0)
#     # usmeteors = IntField(required=True, default=0)
#     created_at = DateTimeField(default=datetime.datetime.now)

from mongoengine import Document, StringField, IntField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField
import datetime

class PrizeDetail(EmbeddedDocument):
    prize_id = StringField(required=True)
    title = StringField(required=True)
    term_conditions = StringField()
    image = StringField()
    required_meteors = IntField(required=True)
    product_uid = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)

class AdminPrizes(Document):
    admin_uid = StringField(required=True, unique=True)
    product_uid = StringField()
    prizes = ListField(EmbeddedDocumentField(PrizeDetail))


    meta = {"db_alias" : "admin-db", "collection" : "prizes"}