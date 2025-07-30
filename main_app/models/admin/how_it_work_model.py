from mongoengine import StringField , FloatField, DateTimeField, Document

class HowItWork(Document):
    admin_uid= StringField(required= True, unique=True)
    program_id = StringField()
    title1 = StringField()
    desc1 = StringField()
    title2 = StringField()
    desc2 = StringField()
    title3 = StringField()
    desc3 = StringField()

    meta =  {"db_alias" : "admin-db", "collection" : "how-it-work"}
