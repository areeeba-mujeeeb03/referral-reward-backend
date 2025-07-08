from mongoengine import Document , StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField

# class AdvertisementCard(Document):
class AdvertisementCardItem(EmbeddedDocument):
    admin_uid = StringField(required=True)
    title = StringField()
    description = StringField()
    button_txt = StringField()
    image_url = StringField()

class AdminAdvertisementCard(Document):
    admin_uid = StringField(required=True, unique=True)
    advertisement_cards = ListField(EmbeddedDocumentField(AdvertisementCardItem))

    meta = {"db_alias" : "admin-db", "collection" : "advertisement-card"}

