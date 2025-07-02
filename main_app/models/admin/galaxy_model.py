from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField, IntField, \
    DynamicDocument
import datetime

class Galaxy(DynamicDocument):
    galaxy_name = StringField(required=True, unique=True)
    total_milestones = IntField()
    all_milestones = ListField(DictField())

    meta = {"db_alias" : "admin-db", 'collection': 'galaxy_milestones'}
