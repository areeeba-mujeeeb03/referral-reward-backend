from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField, IntField, \
    DynamicDocument, EmbeddedDocumentField, EmbeddedDocument
import datetime

class Milestone(EmbeddedDocument):
    milestone_id = StringField(required=True)
    milestone_name = StringField()
    meteors_required_to_unlock = IntField()
    milestone_reward = IntField()
    milestone_description = StringField()
    image = StringField()

class Galaxy(Document):
    galaxy_name = StringField(required=True, unique=True)
    total_meteors_required = IntField()
    highest_reward = StringField()
    total_milestones = IntField()
    stars_to_be_achieved = IntField()
    all_milestones = ListField(EmbeddedDocumentField(Milestone))
    admin_uid = StringField(required=True)

    meta = {"db_alias" : "admin-db", 'collection': 'galaxy_milestones'}
