
from mongoengine import Document, StringField, DictField, ListField , EmbeddedDocument, EmbeddedDocumentField
import datetime

class ExclusivePerks(EmbeddedDocument):
    perk_id = StringField(required=True)
    title = StringField()
    information = StringField()
    image = StringField()
    term_conditions = StringField()

class Perks(Document):
    admin_uid = StringField()
    program_id = StringField()
    perks =  ListField(EmbeddedDocumentField(ExclusivePerks))


    meta = {"db_alias" : "admin-db", "collection" : "exclusive_perks"}

# --------------------------------------------------------------------------


# --- Footer Model
# class FooterSection(Document):
#     admin_uid = StringField(required=True)
#     program_id = StringField()
#     footer_text = StringField()

    meta = { "db_alias": "admin-db", "collection": "footer" }

