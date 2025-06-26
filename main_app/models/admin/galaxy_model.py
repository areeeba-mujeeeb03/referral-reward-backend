from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField
import datetime

class Galaxy(Document):
    total_galaxies = StringField(required=True, unique=True)
    all_galaxies = ListField(DictField)

<<<<<<< HEAD
    meta = {"db_alias" : "admin-db", 'collection': 'galaxy_milestones'}
=======
    meta = {'db_alias' : 'admin-db' , 'collection': 'galaxy_milestones'}
>>>>>>> 16e33ae1762c16826d81f55eaaffff57d8b569c0
