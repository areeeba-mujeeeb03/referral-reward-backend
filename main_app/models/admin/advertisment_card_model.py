from mongoengine import Document , StringField, DateTimeField

class AdvertismentCard(Document):
    admin_uid = StringField(required=True, unique=True)
    title = StringField()
    description = StringField()
    button_txt = StringField()
    image_url = StringField()

    meta = {"db_alias" : "admin-db", "collection" : "advertisment-card"}

