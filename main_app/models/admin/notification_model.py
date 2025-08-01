# models/notification_model.py
from mongoengine import Document, StringField, DateTimeField, ListField, DictField
import datetime

class PushNotification(Document):
    admin_uid = StringField(required=True)
    program_id = StringField(required= True)
    all_notifications = ListField(DictField())

    meta = { "db_alias": "admin-db", "collection": "push_notifications" }
