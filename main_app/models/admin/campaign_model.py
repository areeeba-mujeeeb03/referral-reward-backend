import uuid

from mongoengine import StringField, Document, EmailField, DateTimeField, ListField, DictField, IntField


class Campaign(Document):
    admin_uid = StringField(required=True)
    program_id = StringField()
    program_name = StringField()
    total_participants = IntField()
    base_url = StringField()
    image = StringField()

    def save(self, *args, **kwargs):
        if not self.program_id:
            self.program_id = str(uuid.uuid4())
        return super(Campaign, self).save(*args, **kwargs)


    meta = {"db_alias" : "admin-db", 'collection': 'Campaigns'}
