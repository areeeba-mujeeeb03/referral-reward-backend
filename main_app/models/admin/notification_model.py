# models/notification_model.py
from mongoengine import Document, StringField, DateTimeField, ListField
import datetime

class PushNotification(Document):
    admin_uid = StringField(required=True)
    # notification_uid = StringField(required=True)
    title = StringField(required=True)
    message = StringField(required=True)
    button_text = StringField()
    button_url = StringField()
    segment = StringField(default="All")  # e.g., All or Specific
    specific_users = ListField(StringField())  # user_ids
    schedule_date = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)

    meta = { "db_alias": "admin-db", "collection": "push_notifications" }
