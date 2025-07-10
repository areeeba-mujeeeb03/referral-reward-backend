
from mongoengine import Document, StringField
import datetime

class ExclusivePerks(Document):
    title = StringField()
    information = StringField()
    image = StringField()
    term_conditions = StringField()
    admin_uid = StringField()

    meta = {"db_alias" : "admin-db", "collection" : "exclusive_perks"}
