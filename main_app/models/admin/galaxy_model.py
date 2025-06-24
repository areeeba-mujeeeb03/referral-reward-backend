from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField
import datetime

class Galaxy(Document):
    total_galaxies = StringField(required=True, unique=True)
    all_galaxies = ListField(DictField)

    meta = {'db_alias' : 'admin-db' , 'collection': 'galaxy_milestones'}
