from mongoengine import Document , EmbeddedDocument
from mongoengine.fields import StringField, ListField, EmbeddedDocumentField

# class AdvertisementCard(Document):
class AdvertisementCardItem(EmbeddedDocument):
    title = StringField()
    description = StringField()
    button_txt = StringField()
    image_url = StringField()

class AdminAdvertisementCard(Document):
    admin_uid = StringField(required=True, unique=True)
    advertisement_cards = ListField(EmbeddedDocumentField(AdvertisementCardItem))

    meta = {"db_alias" : "admin-db", "collection" : "advertisement-card"}

