from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField, IntField, \
    DynamicDocument
import datetime

class Galaxy(DynamicDocument):
    admin_uid = StringField(required=True,unique=True)
    galaxy_name = StringField(required=True, unique=True)
    total_meteors_required = IntField(default=0)
    total_milestones = IntField()
    all_milestones = ListField(DictField())

    meta = {"db_alias" : "admin-db", 'collection': 'galaxy_milestones'}
