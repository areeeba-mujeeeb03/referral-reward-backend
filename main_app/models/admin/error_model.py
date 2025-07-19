from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime

class Errors(Document):
    admin_uid = StringField()
    program_id = StringField()
    username = StringField(required=True)
    email = StringField(required=True)
    error_type = StringField(required=True)
    error_source = StringField(required=True)
    status = StringField(default="Unresolved")
    generated_at = DateTimeField(default=datetime.now)

    meta = {"db_alias" : "admin-db", "collection" : "errors"}