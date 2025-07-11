
from mongoengine import Document, StringField, ListField , EmbeddedDocument, EmbeddedDocumentField
import datetime

class ExclusivePerks(Document):
    title = StringField()
    information = StringField()
    image = StringField()
    term_conditions = StringField()
    admin_uid = StringField()

    meta = {"db_alias" : "admin-db", "collection" : "exclusive_perks"}



# --------------------------------------------------------------------------


# --- Footer Model
class FooterItem(EmbeddedDocument):
    content = StringField(required=True)
class FooterSection(Document):
    admin_uid = StringField(required=True)
    footer = ListField(EmbeddedDocumentField(FooterItem))

    meta = { "db_alias": "admin-db", "collection": "footer" }

