from mongoengine import StringField, Document, ListField, IntField, \
EmbeddedDocumentField, EmbeddedDocument

class Milestone(EmbeddedDocument):
    milestone_id = StringField(required=True)
    milestone_name = StringField()
    meteors_required_to_unlock = IntField()
    milestone_reward = IntField()
    milestone_description = StringField()

class Galaxy(EmbeddedDocument):
    galaxy_id = StringField(required=True)
    galaxy_name = StringField()
    total_meteors_required = IntField()
    highest_reward = StringField()
    total_milestones = IntField()
    stars_to_be_achieved = IntField()
    milestones = ListField(EmbeddedDocumentField(Milestone))

class GalaxyProgram(Document):
    program_id = StringField(required=True, unique=True)
    admin_uid = StringField(required=True)
    galaxies = ListField(EmbeddedDocumentField(Galaxy))


    meta = {"db_alias" : "admin-db", 'collection': 'galaxy_milestones'}
